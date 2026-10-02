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
