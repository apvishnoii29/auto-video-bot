import os, time, random, subprocess, asyncio, json, requests, urllib.parse
import edge_tts
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CHAR = "Chotu, a cute little brown bear boy with a red cap, child-like character, same face and fur in every scene, 3d pixar cartoon, bright colors, kid friendly"
VOICE = os.getenv("VOICE", "hi-IN-SwaraNeural")   # Hindi voice
EN_VOICE = "en-IN-NeerjaNeural"                  # fallback if translation fails
PITCH = os.getenv("PITCH", "+25Hz")
UNI = "a blue school uniform and backpack"
ROOM = "in a bright classroom with a green chalkboard, wearing a blue school uniform"
CLASS_INTRO = "Hi kids! I'm Chotu Bear, and welcome to my classroom!"
INTRO = "Hi friends! I'm Chotu Bear, and today we have a fun adventure!"
OUTRO = "Great job, friends! Subscribe to Chotu Bear, and see you next time. Bye bye!"
FAIL = [0]

STORIES = [
 ("Chotu Shares His Honey", ["Chotu found a big jar of honey in the forest.", "His friend Bunny was hungry too.", "Chotu shared the honey with Bunny.", "They both smiled. Sharing makes everyone happy!"]),
 ("Chotu and the Rainy Day", ["It was raining, and Chotu felt sad.", "Then he saw a little bird without a home.", "Chotu made a cozy leaf umbrella for the bird.", "Helping others makes rainy days sunny!"]),
 ("Chotu Learns to Say Sorry", ["Chotu accidentally knocked over Fox's blocks.", "Chotu felt bad inside.", "He said, I'm sorry, and helped build them again.", "Saying sorry is brave and kind!"]),
 ("Chotu Brushes His Teeth", ["Chotu did not want to brush his teeth.", "Then a tooth fairy sang a magic song.", "Brush, brush, up and down, all around!", "Now Chotu has a sparkly smile!"]),
]
WORDS = "Apple Ball Cat Dog Elephant Fish Giraffe Hat Ice-cream Juice Kite Lion Moon Nest Orange Pizza Queen Rainbow Sun Tree Umbrella Violin Whale Xylophone Yo-yo Zebra".split()
COLORS = [("red", "apple", "लाल", "सेब"), ("blue", "sky", "नीला", "आसमान"), ("yellow", "sun", "पीला", "सूरज"), ("green", "frog", "हरा", "मेंढक"), ("orange", "orange", "नारंगी", "संतरा"), ("purple", "grapes", "बैंगनी", "अंगूर"), ("pink", "flower", "गुलाबी", "फूल")]
SHAPES = [("circle", "a ball", "गोला", "गेंद"), ("square", "a box", "चौकोर", "डिब्बा"), ("triangle", "a slice of pizza", "तिकोन", "पिज़्ज़ा का टुकड़ा"), ("star", "a star in the sky", "तारा", "आसमान का तारा"), ("heart", "a heart", "दिल", "दिल"), ("rectangle", "a door", "आयत", "दरवाज़ा")]
IT_HI = {"apples": "सेब", "stars": "तारे", "balloons": "गुब्बारे", "fish": "मछलियाँ"}
FRIENDS = ["Mia", "Leo", "Ava", "Noah", "Zoe", "Sam"]
PLAY = [("playing tag in the playground", "tag"), ("building a tall block tower", "blocks"), ("skipping rope", "jump rope"), ("playing hide and seek", "hide and seek"), ("kicking a soccer ball", "soccer"), ("drawing with colorful chalk", "chalk art")]
FOOD = ["a cheese sandwich", "yummy pasta", "fresh apple slices", "a banana and crackers"]
EVE = [("making a paper airplane", "paper airplanes"), ("painting a rainbow", "painting"), ("building with toy blocks", "blocks"), ("planting a tiny flower", "planting")]

HI = {
 INTRO: "नमस्ते दोस्तों! मैं छोटू भालू हूँ, और आज हम एक मज़ेदार सैर पर चलेंगे!",
 CLASS_INTRO: "नमस्ते बच्चों! मैं छोटू भालू हूँ, मेरी क्लास में आपका स्वागत है!",
 OUTRO: "शाबाश दोस्तों! छोटू भालू को सब्सक्राइब करना न भूलना। फिर मिलेंगे, बाय बाय!",
}

def hi(text):
    if text in HI:
        return HI[text]
    try:
        from deep_translator import GoogleTranslator
        h = GoogleTranslator(source="en", target="hi").translate(text)
        if h:
            HI[text] = h
            return h
    except Exception as e:
        print("translate fallback:", e)
    return None

def story():
    k = os.getenv("GEMINI_API_KEY")
    if k:
        try:
            p = ("Write a new original 30-second story for kids aged 2-6 in simple English, starring Chotu Bear, a kind little bear cub. "
                 'No fear, no violence. 4 or 5 short lines, ending with a gentle moral. Return only JSON: {"title":"","lines":["",""]}')
            m = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}",
                              json={"contents": [{"parts": [{"text": p}]}], "generationConfig": {"responseMimeType": "application/json"}}, timeout=60)
            d = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
            assert d["title"] and len(d["lines"]) >= 3
            return d["title"], d["lines"][:5]
        except Exception as e:
            print("AI story fallback:", e)
    return random.choice(STORIES)

def lesson():
    kind = random.choice(["letter", "number", "color", "shape"])
    if kind == "letter":
        i = random.randrange(26); c = chr(65 + i); w = WORDS[i]
        en = [f"Today's letter is {c}.", f"{c} says {c.lower()}, {c.lower()}, {c.lower()}.", f"{c} is for {w}!", f"Can you say {w}? Great!"]
        HI.update(zip(en, [f"आज का अक्षर है {c}.", f"{c} बोलता है {c.lower()}, {c.lower()}, {c.lower()}.", f"{c} for {w}!", f"क्या तुम {w} बोल सकते हो? शाबाश!"]))
        return (f"Letter {c} for {w}", en,
                [f"the big letter {c} on the chalkboard", f"pointing at the big letter {c}", f"holding a {w} next to the letter {c}", f"happy with a {w}"])
    if kind == "number":
        n = random.randint(2, 10); it = random.choice(["apples", "stars", "balloons", "fish"])
        en = [f"Today we learn the number {n}.", f"Let's count {n} {it} together!", ", ".join(str(x) for x in range(1, n + 1)) + "!", f"{n} {it}! Awesome!"]
        HI.update(zip(en, [f"आज हम नंबर {n} सीखेंगे.", f"चलो मिलकर {n} {IT_HI[it]} गिनते हैं!", en[2], f"{n}! बहुत बढ़िया!"]))
        return (f"Let's Count to {n}", en,
                [f"the big number {n} on the chalkboard", f"{n} cute {it} on a table", f"counting {n} {it} with fingers", f"cheering with {n} {it}"])
    if kind == "color":
        c, o, ch, oh = random.choice(COLORS)
        en = [f"Today we learn the color {c}.", f"{c.title()} is the color of a {o}.", f"Can you find something {c} around you?", f"{c.title()}! Wonderful!"]
        HI.update(zip(en, [f"आज हम {ch} रंग सीखेंगे, यानी {c}.", f"{ch} रंग {oh} का होता है.", f"क्या तुम अपने आसपास कुछ {ch} ढूँढ सकते हो?", f"{c}! शानदार!"]))
        return (f"Learn the Color {c.title()}", en,
                [f"a big {c} paint splash", f"a {c} {o}", f"looking around for {c} things", f"smiling with a {c} {o}"])
    s, o, sh_, oh = random.choice(SHAPES)
    en = [f"Today we learn the {s}.", f"A {s} looks like {o}.", f"Can you draw a {s} in the air?", f"{s.title()}! Super job!"]
    HI.update(zip(en, [f"आज हम {sh_} यानी {s} आकार सीखेंगे.", f"{sh_} {oh} जैसा दिखता है.", f"क्या तुम हवा में {sh_} बना सकते हो?", f"{s}! बहुत बढ़िया!"]))
    return (f"Learn the {s.title()} Shape", en,
            [f"a big {s} drawn on the chalkboard", f"{o} next to a {s}", f"drawing a {s} in the air", f"smiling next to a {s}"])

INC = {
 "classroom": [
  [("Oh no! {g} lost a crayon and looks sad.", "a kid friend looking sad, searching a desk for a crayon"), ("Chotu looks around and finds it under the desk!", "Chotu holding up a crayon he found under the desk, smiling"), ("{g} says thank you. Helping friends feels so good!", "a kid hugging Chotu happily")],
  [("Oops! Some paint spilled on the table during art time.", "colorful paint spilled on a classroom table, kids surprised"), ("Chotu and {f} grab a cloth and clean it up together.", "Chotu and a kid friend wiping the table with a cloth"), ("The teacher smiles. Teamwork makes cleaning easy!", "a smiling teacher giving a thumbs up, clean table")],
  [("A new friend joins the class today, and {g} feels shy.", "a shy new kid standing at the classroom door with a backpack"), ("Chotu waves and says, Hi! Come sit with us!", "Chotu waving and inviting the new kid to sit"), ("Soon everyone is smiling. Being kind makes new friends!", "kids smiling together at a table")],
  [("The teacher asks a question, and Chotu is not sure.", "Chotu thinking with a finger on his chin"), ("{f} whispers a small hint, and Chotu tries his best.", "Chotu bravely raising his hand"), ("He gets it right! Trying again and again makes us smart!", "the teacher clapping, Chotu happy")],
  [("{g} forgot a pencil at home and feels worried.", "a kid looking worried with an empty pencil case"), ("Chotu shares his extra pencil with {g}.", "Chotu handing a pencil to a friend"), ("Sharing is caring! Now they draw together.", "two kids smiling and drawing together")],
 ],
 "playground": [
  [("Oh no! {g} slipped and sat down on the grass.", "a kid sitting on the grass in a playground, looking surprised"), ("Chotu helps {g} up and tells the teacher.", "Chotu holding a friend's hand to help them stand up"), ("The teacher helps, and soon {g} is smiling again. We always help our friends!", "a kind teacher and kids smiling in the playground")],
  [("Everyone wants to go on the slide first.", "kids crowding near a playground slide"), ("Chotu says, Let's take turns!", "Chotu showing kids how to stand in a line"), ("One by one, everyone slides and laughs. Taking turns is fair!", "kids sliding happily down a slide")],
  [("The ball rolled far away across the playground!", "a ball rolling away in a playground"), ("Chotu and {f} run to get it together.", "Chotu and a kid friend running after a ball"), ("They bring it back and high-five. Teamwork is fun!", "kids high-fiving and holding a ball")],
 ],
}

def incident(place, f, g):
    ctx = ROOM if place == "classroom" else "in a sunny school playground, wearing a blue school uniform"
    k = os.getenv("GEMINI_API_KEY")
    if k:
        try:
            p = (f"Write a small, gentle {place} incident in a primary school featuring Chotu Bear and his friends {f} and {g}, for kids aged 2-6. "
                 "Positive, no fear, no violence, ending with a kind lesson. "
                 'Return only JSON: {"scenes":[{"line":"one short sentence","img":"short visual description"},{"line":"","img":""},{"line":"","img":""}]}')
            m = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={k}",
                              json={"contents": [{"parts": [{"text": p}]}], "generationConfig": {"responseMimeType": "application/json"}}, timeout=60)
            d = json.loads(r.json()["candidates"][0]["content"]["parts"][0]["text"])
            sc = [(x["line"], x["img"]) for x in d["scenes"] if x["line"] and x["img"]][:4]
            assert len(sc) >= 3
            return [(l, f"{ctx}, {i}") for l, i in sc]
        except Exception as e:
            print("AI incident fallback:", e)
    return [(l.format(f=f, g=g), f"{ctx}, {i.format(f=f, g=g)}") for l, i in random.choice(INC[place])]

def school():
    f, g = random.sample(FRIENDS, 2)
    play, pn = random.choice(PLAY); food = random.choice(FOOD); eve, en = random.choice(EVE)
    lt, ll, li = lesson()
    S = [
     ("Good morning everyone! It's a sunny morning, and Chotu wakes up with a big yawn.", "waking up in bed wearing pajamas, sunny bedroom window"),
     ("Today is a school day! Chotu is so excited to see his friends.", "jumping happily next to his bed wearing pajamas"),
     ("First, Chotu brushes his teeth. One, two, three! Sparkly clean!", "brushing teeth in the bathroom wearing pajamas"),
     ("Now it's time to put on his school uniform and pack his bag.", f"putting on {UNI} in the bedroom"),
     ("Chotu eats a yummy breakfast. Yum yum yum!", "eating breakfast at the kitchen table wearing a school uniform"),
     ("Beep beep! Here comes the big yellow school bus!", f"waiting at the bus stop wearing {UNI}, a big yellow school bus arriving"),
     (f"On the bus, Chotu says hi to his friends {f} and {g}.", f"sitting in a yellow school bus with two kid friends, wearing {UNI}"),
     ("Welcome to class! Chotu sits at his desk and listens to the teacher.", f"sitting at a small desk in a classroom with kids, wearing {UNI}"),
     (f"Today's lesson is: {lt}.", f"{ROOM}, kids watching, the lesson on the chalkboard"),
    ] + [(l, f"{ROOM}, with kids, {x}") for l, x in zip(ll, li)] + incident("classroom", f, g) + [
     ("Great learning, everyone! Now it's recess time!", "running out of the classroom happily with kids, wearing a school uniform"),
     (f"Chotu, {f} and {g} love {pn}! Come and play with us!", f"{play} with two kid friends in a sunny playground"),
     ("Everyone is laughing and having so much fun together!", "laughing with kid friends in a sunny playground"),
     ] + incident("playground", f, g) + [
     (f"Lunch time! Chotu has {food}, and he shares with {g}. Sharing is caring!", f"eating {food} at a lunch table and sharing with a kid friend"),
     ("After lunch, it's story time. Everyone listens carefully.", "sitting in a circle on a carpet with kids, listening to a teacher reading a book"),
     ("Ring ring! School is over. Time to go home!", f"waving goodbye to the teacher and kids at the school gate, wearing {UNI}"),
     ("Chotu hops on the yellow bus and waves goodbye to his friends.", "waving from a yellow school bus window"),
     ("Back home, Chotu changes into comfy clothes and has a cozy snack.", "at home wearing a comfy t-shirt and shorts, eating a snack"),
     (f"Now Chotu loves {eve}. Can you try it too?", f"{eve} at home wearing comfy clothes"),
     ("What a wonderful day! Chotu puts on his pajamas and gets into bed.", "in pajamas getting into bed, moon outside the window"),
     ("Good night, friends! Sweet dreams, and see you tomorrow at school!", "sleeping peacefully in bed with a teddy bear, moon and stars"),
    ]
    return f"Chotu Goes to School: {lt}", [s[0] for s in S], [s[1] for s in S]

def sh(*a):
    subprocess.run(a, check=True, capture_output=True)

def dur(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True)
    return float(r.stdout.strip())

def ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

def image(prompt, path, w, h):
    u = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(prompt) + f"?width={w}&height={h}&nologo=true&seed=777"
    for a in range(3):
        try:
            r = requests.get(u, timeout=120)
            r.raise_for_status()
            open(path, "wb").write(r.content)
            return
        except Exception as e:
            print("image retry:", e)
            time.sleep(8)
    FAIL[0] += 1
    sh("ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c=0xf59e0b:s={w}x{h}", "-frames:v", "1", path)

def main():
    key = os.getenv("NICHE") or random.choice(["chotu", "class"])
    long = key == "school"
    W, H = (1280, 720) if long else (1080, 1920)
    if long:
        title, scenes, imgs = school()
        cat, tags = "27", ["ChotuGoesToSchool", "SchoolForKids", "KidsLearning", "KidsCartoon", "ToddlerLearning"]
        imgs = [f"{CHAR}, {x}" for x in imgs]
    elif key == "class":
        title, lines, imgs = lesson()
        cat, tags = "27", ["LearnABC", "PreschoolLearning", "ToddlerLearning", "Alphabet"]
        scenes = [CLASS_INTRO] + lines + [OUTRO]
        wave = f"{CHAR}, {ROOM}, waving"
        imgs = [wave] + [f"{CHAR}, {ROOM}, {x}" for x in imgs] + [wave]
    else:
        title, lines = story()
        cat, tags = "24", ["BedtimeStories", "KidsStories", "StoriesForKids"]
        scenes = [INTRO] + lines + [OUTRO]
        wave = f"{CHAR}, waving happily in a sunny forest"
        imgs = [wave] + [f"{CHAR}, {l}" for l in lines] + [wave]
    clips, srt, t = [], [], 0.0
    for i, text in enumerate(scenes):
        img, mp3, mp4 = f"i{i}.jpg", f"a{i}.mp3", f"c{i}.mp4"
        image(imgs[i] + (", wide" if long else ", vertical"), img, W, H)
        spoken = hi(text)
        v = VOICE if spoken else EN_VOICE
        asyncio.run(edge_tts.Communicate(spoken or text, v, pitch=PITCH).save(mp3))
        d = dur(mp3) + 0.5
        n = int(d * 25) + 1
        sh("ffmpeg", "-y", "-i", img, "-i", mp3, "-vf",
           f"scale={int(W * 1.25)}:{int(H * 1.25)},zoompan=z='min(zoom+0.0008,1.2)':d={n}:s={W}x{H}:fps=25,format=yuv420p",
           "-t", str(d), "-c:v", "libx264", "-c:a", "aac", mp4)
        clips.append(mp4)
        srt.append(f"{i + 1}\n{ts(t)} --> {ts(t + d)}\n{text}\n")
        t += d
    if FAIL[0] > len(scenes) // 3:
        raise SystemExit("Too many images failed, not uploading a poor video. Run again later.")
    open("list.txt", "w").write("".join(f"file '{c}'\n" for c in clips))
    open("subs.srt", "w", encoding="utf-8").write("\n".join(srt))
    sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt", "-c", "copy", "joined.mp4")
    mv = 25 if long else 120
    sh("ffmpeg", "-y", "-i", "joined.mp4", "-vf",
       f"subtitles=subs.srt:force_style='FontName=Noto Sans,FontSize=12,Alignment=2,MarginV={mv},Outline=2'",
       "-c:a", "copy", "final.mp4")

    tags = ["KidsLearning", "ChotuBear", "KidsCartoon", "HindiKids"] + ([] if long else ["Shorts"]) + tags
    hashtags = " ".join("#" + x for x in tags[:6])
    body_txt = "Join Chotu Bear for a fun day at school! Learn, play and have fun with friends." if long else "\n".join(scenes[1:-1])
    desc = f"{title}\n\n{body_txt}\n\nSubscribe to Chotu Bear for new videos every day!\n\n{hashtags}"
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"],
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token")
    yt = build("youtube", "v3", credentials=creds)
    full = f"{title} | Chotu Bear" + ("" if long else " #Shorts")
    body = {"snippet": {"title": full[:95], "description": desc, "tags": tags, "categoryId": cat},
            "status": {"privacyStatus": os.getenv("PRIVACY", "private"), "selfDeclaredMadeForKids": True}}
    r = yt.videos().insert(part="snippet,status", body=body,
                           media_body=MediaFileUpload("final.mp4", resumable=True)).execute()
    print("uploaded:", r["id"])
    if long:
        try:
            yt.thumbnails().set(videoId=r["id"], media_body=MediaFileUpload("i7.jpg")).execute()
        except Exception as e:
            print("thumbnail skipped:", e)

main()
