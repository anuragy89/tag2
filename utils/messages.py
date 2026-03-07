"""
messages.py – Large, easily-extensible message template library.

Every list can be extended freely.  The helper `get_msg()` picks
a random entry so tagging always feels fresh.
"""

import random
from typing import Optional

# ══════════════════════════════════════════════════════════════════════════════
#  1.  HITAG  –  Hindi only  (funny + flirty + normal)
# ══════════════════════════════════════════════════════════════════════════════
HITAG_MSGS = [
    "अरे {mention} भाई! तू कहाँ गायब है? 😜 ग्रुप याद कर रहा था तुझे! 💕",
    "ओए {mention}! सो रहे हो क्या? 😴 उठो उठो, ग्रुप में आओ! 🔔",
    "{mention} जी, आपकी याद आई तो बुला लिया 😍 अब मत जाना! 🙏",
    "भाई {mention}, तू ऑनलाइन क्यों नहीं है? 🤔 हम बिना तेरे अधूरे हैं! 💔",
    "{mention} आ जा यार, बहुत बोर हो रहा हूँ 😩 तू होता है तो मज़ा आता है! 🎉",
    "अरे {mention}! कहाँ हो भई? 👀 ग्रुप में लाश की तरह पड़े हो 😂",
    "{mention} तुझे देखकर दिल खुश हो जाता है 😊 आ जा यार! 🌟",
    "यार {mention}, तू बिना बताये गायब हो गया? 😡 आ सामने! 👊",
    "{mention} जी! नमस्ते 🙏 आज कैसा महसूस कर रहे हो? बताओ! 😄",
    "भई {mention}, इश्क में गिरफ्तार हो गए क्या? 💘 ग्रुप में भी आओ! 😂",
    "{mention} ओ मेरे दिल के चैन 💓 कहाँ हो? ग्रुप तेरे बिना सूना है 😢",
    "अरे भाई {mention}! टैग किया तो कम से कम रिप्लाई तो दो 😤 वरना गुस्सा हो जाऊँगा! 😠",
    "{mention} तू है तो महफ़िल है वरना सब बेकार है 🥺 आ जा ना! 💫",
    "भाई {mention}, ग्रुप का सितारा कब चमकेगा? ⭐ आ जा अब! 😄",
    "{mention} जी आपको बहुत याद किया जा रहा है 🫶 दर्शन दो! 😂",
    "ओए {mention}! फ़ोन रख, ग्रुप में आ 📵 यहाँ भी लोग हैं तेरे! 😜",
    "{mention} यार सुन, तू नहीं आया तो हम सब चले जाएँगे 😂 अब तो आ! 🏃",
    "भई {mention}! इस ग्रुप में तेरी बहुत जरूरत है 🌈 आ जा जल्दी! 💨",
    "{mention} किसी की याद में खोये हो? 😏 हम भी तो हैं यहाँ! 😘",
    "यार {mention}, तू आएगा तो सब खुश हो जाएंगे 🎊 अभी आ! 😆",
    "{mention} भाई! टैग देख के भी नहीं आए? दिल तोड़ दिया 💔 आओ ना! 🥺",
    "अरे {mention}! हम इंतज़ार कर रहे हैं 🕐 जल्दी आओ! 🏃‍♂️",
    "{mention} जी, तुम्हारी एक झलक के लिए तरस रहे हैं 😍 आओ! 🌺",
    "भाई {mention}! ग्रुप में आ, नहीं तो मैं रोने लगूँगा 😭 Kidding! 😂 लेकिन आ जा!",
    "{mention} तेरे जैसा कोई नहीं इस ग्रुप में 🏆 इसीलिए बुला रहा हूँ! 😊",
]

# ══════════════════════════════════════════════════════════════════════════════
#  2.  ENTAG  –  English only  (funny + flirty + normal)
# ══════════════════════════════════════════════════════════════════════════════
ENTAG_MSGS = [
    "Hey {mention}! Where have you been hiding? 👀 The group misses you! 💕",
    "{mention} bestie! Stop ignoring us 😤 We see you online! 😂",
    "Paging {mention}! Your presence is required immediately 📢 Don't make us beg! 🙏",
    "Oi {mention}! Wake up, sleeping beauty! 😴 The group needs your energy! ✨",
    "{mention} you absolute legend 🏆 Get in here and bless us with your presence! 👑",
    "Hey {mention}! Are you lost? 😅 Come back to reality – we're here! 🌍",
    "{mention} darling 💖 We've been waiting for you forever. Just saying! 😘",
    "Excuse me {mention}? Yeah you. Come here. 😏 We need to talk. (It's fun, promise!) 🎉",
    "{mention} why are you so quiet lately? 🤫 The group is getting worried! 🥺",
    "Hello there {mention}! Fancy seeing your name here haha 😂 Come chat! 💬",
    "{mention} you traitor! How dare you ghost us 😩 Come back instantly! 💔",
    "Tag! You're it, {mention}! 🏷️ Now it's your turn to be active! 😄",
    "{mention} the vibes are OFF without you 🫶 Please come fix them! 🔧",
    "Good news, {mention}! You've been personally selected to join this chat 😂 Come! 🎊",
    "{mention} babe 💅 the group isn't the same without you. Facts. 💯",
    "PSST! {mention}! Over here! 👋 Yes, YOU! Come join us! 🥳",
    "{mention} I bet you're smiling right now 😊 Now come share that smile with us! 😁",
    "Alert! Alert! {mention} has been detected offline! 🚨 Activating tag protocol! 📡",
    "{mention} you're literally the missing puzzle piece here 🧩 Get in here! 🏃",
    "Hey {mention}! Life is short, come be chaotic with us 🤪 No refunds though! 😂",
    "{mention} your fan club is waiting 🙋‍♂️🙋‍♀️ Please don't keep them waiting! 💫",
    "Knock knock {mention}! Who's there? Your entire group 😂 Open up! 🚪",
    "{mention} we literally googled 'how to summon someone' and tagging was step 1 😅",
    "Dear {mention}, consider this your official VIP invitation 🎟️ Come on in! 🌟",
    "{mention} if you don't reply I'm calling it ghosting and filing a complaint 😤😂",
]

# ══════════════════════════════════════════════════════════════════════════════
#  3.  GMTAG  –  Hinglish Good Morning  (funny + flirty)
# ══════════════════════════════════════════════════════════════════════════════
GMTAG_MSGS = [
    "Good Morning {mention}! ☀️ Uthh jao yaar, zindagi bahut chhoti hai 😂 Aaj kuch toh karo! 🌟",
    "{mention} Good Morning! 🌅 Chai pi lo, life set hai 😄 Aaj ka din tumhara hai! 💪",
    "Subh savere {mention} ko tag karna padta hai 😅 Good Morning bhai! ☀️ Smile karo! 😊",
    "Good Morning {mention}! 🌸 Neend toot gayi? Ab toh uthh jao yaar 😂 We're waiting! 👀",
    "{mention} wakey wakey! 🔔 Good Morning! Sun nikal aaya, tum kab nikloge? 😜☀️",
    "Arre {mention}! Good Morning 🌞 Bhai subha subha miss kiya tumhe! 😍",
    "{mention} good morning! 🌺 Aaj ka din super duper amazing ho tumhara! 💫 Bas active raho! 😄",
    "Rise and shine {mention}! ⭐ Good Morning! Uthh ke group mein aao na please! 🙏😂",
    "{mention} GM! 🌈 Aaj tum bahut cute lag rahe ho (invisibly 😂) Good Morning! 💕",
    "Hey {mention}! Good morning! 🌻 Subah ki pehli tag tujhe hi dedi 😘 Special feel karo! 😁",
    "{mention} GM bhai! ☕ Chai ya coffee? Jaldi batao aur group mein active ho jao! 😄",
    "Good morning {mention}! 🌷 Kal raat soya tha ya phone chalata raha? 😏 Bata bata! 😂",
    "{mention} Good Morning! 🦋 Aaj kuch naya karo, khud ko surprise karo! 🌟 We believe in you!",
    "Subah bhai {mention} ko poora pyaar! 🥰 Good Morning! Smile with teeth today! 😁",
    "{mention}!! Good Morning!! 🎉 Today is going to be EPIC! Trust me! ✨ Ab uth jao! 😂",
    "GM {mention}! 🌝 Raat bhar kya sapne dekhe? Humein bhi batao! 😂 Good morning! 🌅",
    "{mention} Good Morning! 🌼 Ek kaam karo – uthho, smile karo aur group mein aao! 🔥",
    "Subh Prabhat {mention} ji! 🙏 Good Morning! Bhagwan kare aaj ka din best ho! 🌟😄",
    "{mention} GM! ☀️ Neend aachi aayi? Ya phir raat bhar group scroll karte rahe? 😂💕",
    "Hey {mention}! 🌸 Good morning! Tum khush ho toh duniya khush hai! 😊 Smile karo! ✨",
]

# ══════════════════════════════════════════════════════════════════════════════
#  4.  GNTAG  –  Hinglish Good Night  (funny + flirty)
# ══════════════════════════════════════════════════════════════════════════════
GNTAG_MSGS = [
    "Good Night {mention}! 🌙 Aaj ka din kaisa gaya? Kal fir milenge! 😊✨",
    "{mention} so jaao ab! 😴 Good Night! Sapne mein bhi group yaad aaye 😂🌟",
    "GN {mention}! 🌃 Kal phir milenge, tab tak take care! 💕 Meethe sapne! 🌹",
    "{mention} Shubh Raatri! 🌙 Kal subah bhi tag karenge, darr mat 😂 Jao so jao! 😴",
    "Good Night {mention}! 🌠 Aaj bhot kaam kiya? Ya phone chalate rahe? 😏 So jao ab! 😂",
    "{mention} GN! 💫 Tum jahan bhi ho, kal phir yahan aana! 🙏 Miss karenge! 🥺",
    "Hey {mention}! Good Night! 🌜 Phone rakh do, neend important hai! 💤 Or raho? 😄",
    "{mention} Raatri Shubh ho! ⭐ Aaj ke liye shukriya group ka hissa hone ke liye 🫶",
    "GN {mention}! 🌙 Sapne mein hum aayenge... just kidding 😂 Sleep well! 😴💕",
    "{mention} abhi bhi jaag rahe ho? 😤 Good Night! So jao please 🙏 Kal baat karte hain!",
    "Good Night {mention}! 🌌 Kal phir ek nayi subah hogi, new energy ke saath! 🌅✨",
    "{mention} GN! 🌛 Aaj bahut hasaye, kal bhi hasana mat bhoolna! 😄💛",
    "Hey {mention}! 🌙 Raat ko phone mat chalana 😅 But agar chala bhi rahe ho, GN! 😂✨",
    "{mention} Good Night! 💙 Duniya ki chinta mat karo, bas aaram karo! 😌🌟",
    "GN {mention}! 🌠 Sapne mein princess/prince ayenge 😏 Jao so jao ab! 😂💕",
    "{mention} Shubh Ratri! 🌙 Kal phir tagenge, ab so jao 😄 Take care! 🫶",
    "Good Night {mention}! 🌃 Aaj group mein active rehne ka shukriya! Miss you already! 💔😂",
    "{mention} GN yaar! 🌜 Khayal rakhna apna! Kal milte hain fresh hokar! 🌟✨",
    "Hey {mention}! 😴 Phone neeche rakh, aankhein band karo, so jao! Good Night! 🌙💤",
    "{mention} GN! 🌌 Aaj ki raat ki sabse special tag tumhe 😘 Meethe sapne! 💫",
]

# ══════════════════════════════════════════════════════════════════════════════
#  5.  TAGALL  –  Hinglish general  (funny + flirt + meme + normal)
# ══════════════════════════════════════════════════════════════════════════════
TAGALL_MSGS = [
    "{mention} bhai! 👀 Idhar aa, group mein kuch interesting ho raha hai! 🎉",
    "Arey {mention}! Group mein life hai, phone mein nahi 😂 Aa jao! 🌟",
    "{mention} teri yaad aayi toh tag kar diya 😂 Ab aaja yaar! 💕",
    "Yo {mention}! 🤙 Kya chal raha hai life mein? Bata na! 😄",
    "{mention} tune abhi tak reply nahi kiya? 😤 Bhai ye kya hua? 😂",
    "Arre yaar {mention}! Tum bina bataye gum ho gaye 😩 Wapas aao! 🙏",
    "{mention} 💀 Bhai/Behen, are you alive? Proof chahiye 😂 React karo!",
    "Listen {mention}! 📣 Ye group tumhare bina incomplete hai! Sach mein! 💯",
    "{mention} main teri waajah se yahan hoon tumhe tag karne 😂 Ab kush ho jao! 😊",
    "Oops! {mention} ka naam aa gaya list mein 😅 Toh aa hi jao na! 🎊",
    "{mention} yaar kitna wait karein? 🕐 Aa jao please! 🥺",
    "Tag! 🏷️ {mention}! Tumhari baari hai active hone ki! 😄 Let's go! 🚀",
    "{mention} bhai FOMO mat lo! 😂 Group mein itna sab ho raha hai! Come fast! ⚡",
    "Kahaan ho {mention}? 🔍 Missing person report filed ho gayi 😂 Aao jaldi!",
    "{mention} tum aate ho toh group mein vibe aati hai 🔥 Aa jao please! 💫",
    "Psst! {mention}! 🤫 Secret baat karni hai... group mein aao 😏 Just kidding! 😂",
    "{mention} bhai, duniya gol hai... lekin tum idhar kyun nahi? 😂 Aa jao yaar!",
    "Attention {mention}! 📢 Your presence is strongly requested here! 👑 Welcome!",
    "{mention} without you this group is like chai without sugar ☕ Come sweetennn it! 😂",
    "Oi oi {mention}! 👋 Kya scene hai? Group mein aao, scene bahut acha hai! 🎭",
    "{mention} tujhe dekhke lagta hai ki life mein kuch achha hai 💖 Aa jaa yaar!",
    "Bhai {mention}! Hum sab yahan hain aur tum wahan? 😤 Aao idhar! 🏃",
    "{mention} ab toh aa jao, baat karte hain 😊 Kitna ignore karoge! 😂💕",
    "Hey hey hey {mention}! 🌟 Bas tag kar raha hoon, aage tum jaano 😂 Love ya! 💖",
    "{mention} this message is 100% made with love and 0% spam 😂 Trust me! 😇",
]

# ══════════════════════════════════════════════════════════════════════════════
#  6.  JTAG  –  Hinglish Jokes  (funny + flirty + punny)
# ══════════════════════════════════════════════════════════════════════════════
JTAG_MSGS = [
    "{mention} 😂 Ek banda exam ke pehle bolta hai: 'Bhagwan pe bharosa hai' – Bhagwan: 'Mujh pe mat, book pe kar!' 😂",
    "{mention} Teacher: 'Tum class mein soye kyun?' Student: 'Aap boring the sir!' 😂 Relatable? 😅",
    "Ye joke {mention} ke liye hai 😂 Aadmi ne mirror toda – bola '7 saal bad kismat!' Wife ne suna – boli 'Mujhse shaadi ki, 30 saal bad bhi kismat nahi!' 💀",
    "{mention} sunno! 😂 Wifi ka password maanga ghar pe, uncle bole 'Beta rishte mein aa, tab batate hain!' 🤣",
    "Hahaha {mention}! 😆 Biology teacher: 'Bacteria kahan milte hain?' Student: 'Sir, sabse zyada phone ki screen pe!' 😂 True story!",
    "{mention} 🤣 Ek banda bola: 'Main apna past bhoolna chahta hoon' Doctor: 'To payment mein bhi bhool jaoge?' 💀😂",
    "Joke time {mention}! 😂 Maths: 2+2=4 / English: Two plus two is four / Indian Parent: Yeh 4 kab karega kuch? 😭😂",
    "{mention} 😂 Ek banda driving test mein fail hua 9 baar... Driver bola 'Practice makes perfect' – wo bola 'Mere pedestrians bhi yahi kehte hain!' 💀",
    "Lol {mention} 😂 Student exam mein – 'Describe rain' likha: 'Main nahi jaanta lekin chhat toot rahi thi!' 🤣",
    "{mention} 😂 Doston ke group mein tab tak serious rahein jab tak koi photo share na kare aur sab judge na kare! 😅 Waise tumhara kya haal hai? 😜",
    "Haha {mention}! 🤣 Indian mom ka GPS = Sab kuch jaanti hai lekin ek baar ko yeh nahi puchti 'Khana khaya?' Oops wait – wo toh puchti hi rehti hai! 😂",
    "{mention} funny truth! 😂 Homework karne ke baad jo neend aati hai... woh class mein kyun aati hai? 😴 Science jawaab do!",
    "LOL {mention} 🤣 Bhai ne phone pe game kheli raat bhar – subah papa ne dekha: 'Itni mehnatt padhai mein karo!' Bhai: 😶",
    "{mention} 😂 Desi logic: 'Beta doctor bano' – Beta: 'Kyu?' – 'Kyunki sab kehte hain!' – Beta: 'Toh sab bolo' 😅",
    "Hehe {mention}! 😄 Ek banda marriage ke baad bola: 'Mujhe zindagi mein ek hi darr hai' – kya? – 'Wife ka ek aur number save karna!' 💀😂",
    "{mention} ab hasna mat rokna! 😂 Physics: F = ma / Desi papa: F = Fail = My anger 😅 Run!",
    "Tag alert {mention}! 😂 Akbar-Birbal: 'Birbal, aise do log lao jo kuch na karte hon!' – Birbal laaya – 'Ye doctor aur ye government employee hai!' 💀",
    "Hahhaha {mention}! 😆 Ek banda gym gaya aur bola: 'Mujhe six-pack chahiye!' Trainer: 'Roz aao!' Banda: 'Roz? Main toh photo ke liye aaya tha!' 😂",
    "{mention} 😂 School friends ka group = 24/7 active / Family group = Ek forward aaya, sab ne seen kiya, kisi ne reply nahi kiya 😅",
    "{mention} ye joke genuine nahi hai lekin tag genuine hai! 😂 Ab toh bol do kuch! 🗣️💬",
]

# ══════════════════════════════════════════════════════════════════════════════
#  7.  ADMIN TAG  –  prefix when tagging admins
# ══════════════════════════════════════════════════════════════════════════════
ADMIN_TAG_PREFIX = "📢 **Admin Alert!** Tagging all admins:\n\n"
ADMIN_TAG_SUFFIX = "\n\n⚠️ _Please attend to the matter above._"

# ══════════════════════════════════════════════════════════════════════════════
#  8.  ALL TAG  –  prefix when tagging everyone
# ══════════════════════════════════════════════════════════════════════════════
ALL_TAG_PREFIX = "📣 **Attention Everyone!**\n\n"
ALL_TAG_SUFFIX = "\n\n👆 _Please check the message above!_"

# ══════════════════════════════════════════════════════════════════════════════
#  Welcome messages
# ══════════════════════════════════════════════════════════════════════════════
GROUP_JOIN_MSG = """
🎉 **Hey everyone! I'm alive and kicking!** 🎉

Thanks for adding me to **{chat_title}**! 🙏

I'm your personal **Tag Bot** – here to keep everyone active and entertained! 🔥

➤ Type /help to see all my commands and start tagging! 🏷️

Let's make this group 🔥🔥🔥
"""

# ══════════════════════════════════════════════════════════════════════════════
#  Helper
# ══════════════════════════════════════════════════════════════════════════════
_POOL_MAP = {
    "hitag":  HITAG_MSGS,
    "entag":  ENTAG_MSGS,
    "gmtag":  GMTAG_MSGS,
    "gntag":  GNTAG_MSGS,
    "tagall": TAGALL_MSGS,
    "jtag":   JTAG_MSGS,
}

def get_msg(tag_type: str, mention: str, custom: str = "") -> str:
    """Return a random message for *tag_type*, mention substituted in."""
    pool = _POOL_MAP.get(tag_type, TAGALL_MSGS)
    template = random.choice(pool)
    msg = template.format(mention=mention)
    if custom:
        msg = f"{custom}\n\n{msg}"
    return msg


def build_mention(user_id: int, name: str) -> str:
    return f"[{name}](tg://user?id={user_id})"
