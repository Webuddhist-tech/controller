# -*- coding: utf-8 -*-
import json, io

# Tibetan Uchen + full transliteration for homage, root stanza, and 21 numbered
# praises, from the clean text the user pasted. Structure follows the Tibetan
# source of truth: homage, then root praise (unnumbered), then praises 1-21.
bo = {
  "homage": (
    ["ཨོཾ་རྗེ་བཙུན་མ་འཕགས་མ་སྒྲོལ་མ་ལ་ཕྱག་འཚལ་ལོ། །"],
    ["om jetsünma pakma drolma la chaktsal lo"]),
  "root": (
    ["ཕྱག་འཚལ་ཏཱ་རེ་མྱུར་མ་དཔའ་མོ། །","ཏུཏྟཱ་ར་ཡིས་འཇིགས་པ་སེལ་མ། །",
     "ཏུ་རེས་དོན་ཀུན་སྦྱིན་པས་སྒྲོལ་མ། །","སྭཱ་ཧའི་ཡི་གེ་ཁྱོད་ལ་འདུད་དོ། །"],
    ["chaktsal taré nyurma pamo","tuttara yi jikpa selma",
     "turé dön kün jinpé drolma","sa hé yigé khyö la dü do"]),
  1: (["ཕྱག་འཚལ་སྒྲོལ་མ་མྱུར་མ་དཔའ་མོ། །","སྤྱན་ནི་སྐད་ཅིག་གློག་དང་འདྲ་མ། །",
       "འཇིག་རྟེན་གསུམ་མགོན་ཆུ་སྐྱེས་ཞལ་གྱི། །","གེ་སར་བྱེ་བ་ལས་ནི་བྱུང་མ། །"],
      ["chaktsal drolma nyurma pamo","chen ni kechik lok dang dra ma",
       "jikten sum gön chukyé zhal gyi","gesar jewa lé ni jung ma"]),
  2: (["ཕྱག་འཚལ་སྟོན་ཀའི་ཟླ་བ་ཀུན་ཏུ། །","གང་བ་བརྒྱ་ནི་བརྩེགས་པའི་ཞལ་མ། །",
       "སྐར་མ་སྟོང་ཕྲག་ཚོགས་པ་རྣམས་ཀྱི། །","རབ་ཏུ་ཕྱེ་བའི་འོད་རབ་འབར་མ། །"],
      ["chaktsal tönké dawa küntu","gangwa gya ni tsekpé zhal ma",
       "karma tongtrak tsokpa nam kyi","rabtu chewé ö rab bar ma"]),
  3: (["ཕྱག་འཚལ་སེར་སྔོ་ཆུ་ནས་སྐྱེས་ཀྱི། །","པདྨས་ཕྱག་ནི་རྣམ་པར་བརྒྱན་མ། །",
       "སྦྱིན་པ་བརྩོན་འགྲུས་དཀའ་ཐུབ་ཞི་བ། །","བཟོད་པ་བསམ་གཏན་སྤྱོད་ཡུལ་ཉིད་མ། །"],
      ["chaktsal ser ngo chu né kyé kyi","pemé chak ni nampar gyen ma",
       "jinpa tsöndrü katub zhiwa","zöpa samten chöyul nyi ma"]),
  4: (["ཕྱག་འཚལ་དེ་བཞིན་གཤེགས་པའི་གཙུག་ཏོར། །","མཐའ་ཡས་རྣམ་པར་རྒྱལ་བ་སྤྱོད་མ། །",
       "མ་ལུས་ཕ་རོལ་ཕྱིན་པ་ཐོབ་པའི། །","རྒྱལ་བའི་སྲས་ཀྱིས་ཤིན་ཏུ་བསྟེན་མ། །"],
      ["chaktsal dezhin shekpé tsuktor","tayé nampar gyalwa chö ma",
       "malü parol chinpa tobpé","gyalwé sé kyi shintu ten ma"]),
  5: (["ཕྱག་འཚལ་ཏུཏྟཱ་ར་ཧཱུྃ་ཡི་གེ། །","འདོད་དང་ཕྱོགས་དང་ནམ་མཁའ་གང་མ། །",
       "འཇིག་རྟེན་བདུན་པོ་ཞབས་ཀྱིས་མནན་ཏེ། །","ལུས་པ་མེད་པར་འགུགས་པར་ནུས་མ། །"],
      ["chaktsal tuttara hung yigé","dö dang chok dang namkha gang ma",
       "jikten dünpo zhab kyi nen té","lüpa mepar gukpar nü ma"]),
  6: (["ཕྱག་འཚལ་བརྒྱ་བྱིན་མེ་ལྷ་ཚངས་པ། །","རླུང་ལྷ་སྣ་ཚོགས་དབང་ཕྱུག་མཆོད་མ། །",
       "འབྱུང་པོ་རོ་ལངས་དྲི་ཟ་རྣམས་དང་། །","གནོད་སྦྱིན་ཚོགས་ཀྱིས་མདུན་ནས་བསྟོད་མ། །"],
      ["chaktsal gyajin melha tsangpa","lunglha natsok wangchuk chö ma",
       "jungpo rolang driza nam dang","nöjin tsok kyi dün né tö ma"]),
  7: (["ཕྱག་འཚལ་ཏྲཊ་ཅེས་བྱ་དང་ཕཊ་ཀྱིས། །","ཕ་རོལ་འཕྲུལ་འཁོར་རབ་ཏུ་འཇོམས་མ། །",
       "གཡས་བསྐུམ་གཡོན་བརྐྱང་ཞབས་ཀྱིས་མནན་ཏེ། །","མེ་འབར་འཁྲུག་པ་ཤིན་ཏུ་འབར་མ། །"],
      ["chaktsal tré cheja dang pé kyi","parol trulkhor rabtu jom ma",
       "yé kum yön kyang zhab kyi nen té","mebar trukpa shintu bar ma"]),
  8: (["ཕྱག་འཚལ་ཏུ་རེ་འཇིགས་པ་ཆེན་པོས། །","བདུད་ཀྱི་དཔའ་བོ་རྣམ་པར་འཇོམས་མ། །",
       "ཆུ་སྐྱེས་ཞལ་ནི་ཁྲོ་གཉེར་ལྡན་མཛད། །","དགྲ་བོ་ཐམས་ཅད་མ་ལུས་གསོད་མ། །"],
      ["chaktsal turé jikpa chenpö","dü kyi pawo nampar jom ma",
       "chukyé zhal ni tronyer den dzé","drawo tamché malü sö ma"]),
  9: (["ཕྱག་འཚལ་དཀོན་མཆོག་གསུམ་མཚོན་ཕྱག་རྒྱའི། །","སོར་མོས་ཐུགས་ཀར་རྣམ་པར་བརྒྱན་མ། །",
       "མ་ལུས་ཕྱོགས་ཀྱི་འཁོར་ལོས་བརྒྱན་པའི། །","རང་གི་འོད་ཀྱི་ཚོགས་རྣམས་འཁྲུག་མ། །"],
      ["chaktsal könchok sum tsön chakgyé","sormö tukkar nampar gyen ma",
       "malü chok kyi khorlö gyenpé","rang gi ö kyi tsok nam truk ma"]),
  10:(["ཕྱག་འཚལ་རབ་ཏུ་དགའ་བ་བརྗིད་པའི། །","དབུ་རྒྱན་འོད་ཀྱི་ཕྲེང་བ་སྤེལ་མ། །",
       "བཞད་པ་རབ་བཞད་ཏུཏྟཱ་ར་ཡིས། །","བདུད་དང་འཇིག་རྟེན་དབང་དུ་མཛད་མ། །"],
      ["chaktsal rabtu gawa jipé","ugyen ö kyi trengwa pelma",
       "zhepa rab zhé tuttara yi","dü dang jikten wang du dzé ma"]),
  11:(["ཕྱག་འཚལ་ས་གཞི་སྐྱོང་བའི་ཚོགས་རྣམས། །","ཐམས་ཅད་འགུགས་པར་ནུས་པ་ཉིད་མ། །",
       "ཁྲོ་གཉེར་གཡོ་བའི་ཡི་གེ་ཧཱུྃ་གིས། །","ཕོངས་པ་ཐམས་ཅད་རྣམ་པར་སྒྲོལ་མ། །"],
      ["chaktsal sa zhi kyongwé tsok nam","tamché gukpar nüpa nyi ma",
       "tronyer yowé yigé hung gi","pongpa tamché nampar drolma"]),
  12:(["ཕྱག་འཚལ་ཟླ་བའི་དུམ་བུའི་དབུ་རྒྱན། །","བརྒྱན་པ་ཐམས་ཅད་ཤིན་ཏུ་འབར་མ། །",
       "རལ་པའི་ཁྲོད་ན་འོད་དཔག་མེད་ལས། །","རྟག་པར་ཤིན་ཏུ་འོད་རབ་མཛད་མ། །"],
      ["chaktsal dawé dumbü ugyen","gyenpa tamché shintu bar ma",
       "ralpé trö na öpakmé lé","takpar shintu ö rab dzé ma"]),
  13:(["ཕྱག་འཚལ་བསྐལ་པ་ཐ་མའི་མེ་ལྟར། །","འབར་བའི་ཕྲེང་བའི་དབུས་ན་གནས་མ། །",
       "གཡས་བརྐྱང་གཡོན་བསྐུམ་ཀུན་ནས་བསྐོར་དགའི། །","དགྲ་ཡི་དཔུང་ནི་རྣམ་པར་འཇོམས་མ། །"],
      ["chaktsal kalpa tamé mé tar","barwé trengwé ü na né ma",
       "yé kyang yön kum künné kor gé","dra yi pung ni nampar jom ma"]),
  14:(["ཕྱག་འཚལ་ས་གཞིའི་ངོས་ལ་ཕྱག་གི། །","མཐིལ་གྱིས་བསྣུན་ཅིང་ཞབས་ཀྱིས་བརྡུང་མ། །",
       "ཁྲོ་གཉེར་ཅན་མཛད་ཡི་གེ་ཧཱུྃ་གིས། །","རིམ་པ་བདུན་པོ་རྣམས་ནི་འགེམས་མ། །"],
      ["chaktsal sa zhi ngö la chak gi","til gyi nün ching zhab kyi dung ma",
       "tronyer chen dzé yigé hung gi","rimpa dünpo nam ni gem ma"]),
  15:(["ཕྱག་འཚལ་བདེ་མ་དགེ་མ་ཞི་མ། །","མྱ་ངན་འདས་ཞི་སྤྱོད་ཡུལ་ཉིད་མ། །",
       "སྭཱ་ཧཱ་ཨོཾ་དང་ཡང་དག་ལྡན་པས། །","སྡིག་པ་ཆེན་པོ་འཇོམས་པ་ཉིད་མ། །"],
      ["chaktsal dé ma gé ma zhi ma","nya ngen dé zhi chöyul nyi ma",
       "soha om dang yangdak denpé","dikpa chenpo jompa nyi ma"]),
  16:(["ཕྱག་འཚལ་ཀུན་ནས་བསྐོར་རབ་དགའ་བའི། །","དགྲ་ཡི་ལུས་ནི་རབ་ཏུ་འགེམས་མ། །",
       "ཡི་གེ་བཅུ་པའི་ངག་ནི་བཀོད་པའི། །","རིག་པ་ཧཱུྃ་ལས་སྒྲོལ་མ་ཉིད་མ། །"],
      ["chaktsal künné kor rabga bé","dra yi lü ni rabtu gem ma",
       "yigé chupé ngak ni köpé","rigpa hung lé drölma nyi ma"]),
  17:(["ཕྱག་འཚལ་ཏུ་རེའི་ཞབས་ནི་བརྡབས་པས། །","ཧཱུྃ་གི་རྣམ་པའི་ས་བོན་ཉིད་མ། །",
       "རི་རབ་མནྡ་ར་དང་འབིགས་བྱེད། །","འཇིག་རྟེན་གསུམ་རྣམས་གཡོ་བ་ཉིད་མ། །"],
      ["chaktsal turé zhab ni dabpé","hung gi nampé sabön nyi ma",
       "rirab mendara dang bikjé","jikten sum nam yowa nyi ma"]),
  18:(["ཕྱག་འཚལ་ལྷ་ཡི་མཚོ་ཡི་རྣམ་པའི། །","རི་དྭགས་རྟགས་ཅན་ཕྱག་ན་བསྣམས་མ། །",
       "ཏཱ་ར་གཉིས་བརྗོད་ཕཊ་ཀྱི་ཡི་གེས། །","དུག་རྣམས་མ་ལུས་པར་ནི་སེལ་མ། །"],
      ["chaktsal lha yi tso yi nampé","ridak takchen chak na nam ma",
       "tara nyi jö pé kyi yigé","duk nam malüpar ni selma"]),
  19:(["ཕྱག་འཚལ་ལྷ་ཡི་ཚོགས་རྣམས་རྒྱལ་པོ། །","ལྷ་དང་མིའམ་ཅི་ཡིས་བསྟེན་མ། །",
       "ཀུན་ནས་གོ་ཆ་དགའ་བ་བརྗིད་ཀྱིས། །","རྩོད་དང་རྨི་ལམ་ངན་པ་སེལ་མ། །"],
      ["chaktsal lha yi tsok nam gyalpo","lha dang mi'amchi yi ten ma",
       "künné gocha gawa ji kyi","tsö dang milam ngenpa selma"]),
  20:(["ཕྱག་འཚལ་ཉི་མ་ཟླ་བ་རྒྱས་པའི། །","སྤྱན་གཉིས་པོ་ལ་འོད་རབ་གསལ་མ། །",
       "ཧ་ར་གཉིས་བརྗོད་ཏུཏྟཱ་ར་ཡིས། །","ཤིན་ཏུ་དྲག་པོའི་རིམས་ནད་སེལ་མ། །"],
      ["chaktsal nyima dawa gyepé","chen nyipo la ö rabsal ma",
       "hara nyi jö tuttara yi","shintu drakpö rimné selma"]),
  21:(["ཕྱག་འཚལ་དེ་ཉིད་གསུམ་རྣམས་བཀོད་པས། །","ཞི་བའི་མཐུ་དང་ཡང་དག་ལྡན་མ། །",
       "གདོན་དང་རོ་ལངས་གནོད་སྦྱིན་ཚོགས་རྣམས། །","འཇོམས་པ་ཏུ་རེ་རབ་མཆོག་ཉིད་མ། །"],
      ["chaktsal denyi sum nam köpé","zhiwé tu dang yangdak den ma",
       "dön dang rolang nöjin tsok nam","jompa turé rab chok nyi ma"]),
}

# English meanings, in the FIRST PDF's order (homage-dup, then its Tara 1..21).
# We realign: English "so swift and courageous" -> Tibetan root; English #2 -> ॥1॥ ...
en_by_pdf_index = {
  1:["Homage to Tara, so swift and courageous,","Your eyes flash like lightning, so quick and all-seeing,","Born from the tears of the Lord of Trailokya","At the heart of a beautiful lotus in blossom."],
  2:["Homage to Tara, whose smile is as radiant,","As one hundred million full autumnal moons;","Ablaze with the light of the stars in their thousands,","You shine with a transcendent light of perfection."],
  3:["Homage to Tara, our golden-skinned mother;","Adorning your hand is an azure-blue lotus.","Kind, open-handed, hard-working and patient,","And one with the state of samadhi perfected."],
  4:["Homage to Tara, whose victories are endless,","The crown on the heads of the Tathagatas.","Praised by the masters of all the perfections,","All bodhisattvas rely on your guidance."],
  5:["Homage to Tara, our spellbinding Mother,","You create all of space with your hūṃ and tuttāre,","All beings you magnetize, without exception,","And trample the seven worlds under your feet."],
  6:["Homage to Tara, whom all the gods worship,","Indra, Marut, Agni, Shiva and Brahma;","Praised by the demons who harm and assail us,","Ghosts, spirits, zombies, gandharvas and yakṣas."],
  7:["Homage to Tara, who crushes black magic,","With traṭ and with phaṭ you destroy harmful forces;","You dance, right knee bent and the left leg extended,","All magic consumed in a blazing inferno."],
  8:["Homage to Tara, whose spine-chilling ture","Vanquishes even the powerful Mara;","Wrinkling her beautiful brow in fierce anger,","She crushes all foes and destroys them completely."],
  9:["Homage to Tara, the radiant lady,","You form at your heart the three Rare and Supreme,","Mother, whose radiance fills all directions","With brilliant light that bedazzles all thinking."],
  10:["Homage to Tara, whose sparkling tiara,","Shines with the light of her limitless joy.","Your laughter and tuttāre topple all demons,","Subduing all worlds with exultant delight."],
  11:["Homage to Tara, the Mother who summons","All the world's leaders with hūṃ and a frown.","You free us from hardship, from need and misfortune,","From homelessness, poverty, hunger and thirst."],
  12:["Homage to Tara, whose bright shining tiara,","Is graced with a brilliant crescent new moon.","Sitting amidst your thick mane of black tresses,","Is Lord Amitabha irradiant with light."],
  13:["Homage to Tara, encircled by fire,","Infernos of flames, like the end of all time.","Truth's enemies and their great armies you vanquish,","And spin, right leg stretched with your left leg drawn in."],
  14:["Homage to Tara, who strikes the earth's surface","You pound with your palms and you stamp with your feet;","With hūṃ and a glowering scowl, all your anger","Shatters the underworld's layers, all seven."],
  15:["Homage to Tara, the one who is blissful,","You are liberation, your province is peace,","With oṃ and with svāhā, so perfectly rendered","You lay waste to all the worst evils and sufferings."],
  16:["Homage to Tara, immersed in deep rapture,","You shatter the bodies of all of your foes;","Declaiming your ten letters and hūm of wisdom,","You liberate every suffering being."],
  17:["Homage to Tara, the bold dancing lady,","With ture, you stomp and all obstacles perish,","With hūṃ, Mount Meru, Mandara, and Vindhya,","And the three worlds of existence all tremble."],
  18:["Homage to Tara, who holds in her white hand,","A moon – deer-marked moon – like a heavenly lake;","Expunging all traces of toxins and venom","You purge all the poisons with tāra tāra phaṭ."],
  19:["Homage to Tara, who all the gods count on,","Their kings and their gods and kiṃnaras all trust;","Your armour of joy and contentment is splendid,","It clears away nightmares and soothes away strife."],
  20:["Homage to Tara, whose lustrous eyes sparkle","And shine with the light of the sun and full moon,","Uttering hara hara and tuttāre,","You pacify all the most vicious pandemics."],
  21:["Homage to Tara, who with three tathātās,","Commands all the power she needs to bring peace.","Supreme Ture, you are the one who annihilates,","The hordes of grahas, vetālas, and the yakṣas."],
}
# Sanskrit + English NAME per Tibetan stanza. PDF names are in painting order,
# which matches Tibetan: root=PDF1, ॥1॥=PDF2 ... ॥20॥=PDF21, ॥21॥ has no PDF name.
names_pdf = {
 1:("ARYA-TURE-VIRA-TĀRĀ","Tārā Swift and Heroic"),
 2:("ARYA-SHUKLA-KANTA-TĀRĀ","Tārā White as Autumn Moon"),
 3:("ARYA-KANAKA-VARNA-TĀRĀ","Golden-Colored Tārā"),
 4:("ARYA-TATHAGATOSHNISHI-TĀRĀ","Tārā Victorious Ushnisha"),
 5:("ARYA-HUMKARA-NADINI-TĀRĀ","Tārā Proclaiming the Sound of Hum"),
 6:("ARYA-TRAILOKYA-VIJAYA-TĀRĀ","Tārā Victorious Over the 3 Worlds"),
 7:("ARYA-PRAMARDINI-TĀRĀ","Tārā Crushing Adversaries"),
 8:("ARYA-MARA-MARDANESHVARI-TĀRĀ","Tārā Who Bestows Supreme Powers"),
 9:("ARYA-KHADIRA-VANI-TĀRĀ","Tārā Granter of Boons"),
 10:("ARYA-SHOKA-VINODANI-TĀRĀ","Tārā Dispeller of Sorrow"),
 11:("ARYA-JAGADVASHI-TĀRĀ","Tārā Summoner of Beings"),
 12:("ARYA-MANGALALOKA-TĀRĀ","Tārā Auspiciously Shining"),
 13:("ARYA-PARICHAYIKA-TĀRĀ","Tārā the Ripener"),
 14:("ARYA-BHRIKUTI-TĀRĀ","Tārā with a Frown"),
 15:("ARYA-MAHASHANTA-TĀRĀ","Tārā of Great Peace"),
 16:("ARYA-RAGA-NISHUDANI-TĀRĀ","Tārā Destroyer of Attachment"),
 17:("ARYA-SUKHA-SADHANI-TĀRĀ","Tārā Accomplishing Bliss"),
 18:("ARYA-VIJAYA-TĀRĀ","Victorious Liberating One"),
 19:("ARYA-DUKHA-DAHANI-TĀRĀ","Tārā Burner of Suffering"),
 20:("ARYA-SIDDHI-SAMBHAVA-TĀRĀ","Tārā Source of Siddhis"),
 21:("ARYA-PARINISHPANNA-TĀRĀ","Tārā the Perfecter"),
}

def verse(vid, number, uchen, translit, en, sanskrit, enname, label=None):
    d = {"type":"verse","id":vid}
    if number is not None: d["number"]=number
    if label: d["label"]={"en":label,"zh":"","hi":"","bo":""}
    d["uchen"]="\n".join(uchen)
    d["translit"]=" · ".join([]) or translit[0]  # keep a short label = first rom line
    d["translit_full"]=translit
    d["names"]={"sanskrit":sanskrit,"en":enname}
    d["meaning"]={"en":en,"zh":[],"hi":[],"bo":uchen}
    return d

seq = []
seq.append({"type":"section","id":"refuge","title":{"en":"Refuge","zh":"","hi":"","bo":""}})
seq.append({"type":"section","id":"bodhichitta","title":{"en":"Bodhichitta","zh":"","hi":"","bo":""}})
# Homage (not in loop)
hu,ht = bo["homage"]
seq.append(verse("homage",None,hu,ht,[],"","",label="Opening Homage"))

seq.append({"type":"loop_start","id":"taras_loop","title":{"en":"The 21 Praises (root + 21)","zh":"","hi":"","bo":""}})
# Root praise (repeats with the loop per user's PoC choice; khenpos to confirm)
ru,rt = bo["root"]
seq.append(verse("root",None,ru,rt,en_by_pdf_index[1],names_pdf[1][0],names_pdf[1][1],label="Root Praise"))
# Numbered praises 1..21 -> Tibetan stanza N, English pdf index N+1, name pdf index N+1
for n in range(1,22):
    uu,tt = bo[n]
    en = en_by_pdf_index.get(n+1, [])
    nm = names_pdf.get(n+1, ("",""))
    seq.append(verse(f"praise-{n}", n, uu, tt, en, nm[0], nm[1]))
seq.append({"type":"loop_end","id":"taras_loop_end"})

seq.append({"type":"section","id":"dedication","title":{"en":"Dedication of Merit","zh":"","hi":"","bo":""}})

content = {
  "_README": ("Content for the 21 Praises to Tara puja overlay. TIBETAN IS SOURCE OF TRUTH: "
    "structure is homage, root praise, then 21 numbered praises (Tibetan ॥1॥–॥21॥). "
    "English meanings are realigned to sit under the correct Tibetan stanza. "
    "FIELDS TO FILL: meaning.zh and meaning.hi (empty arrays); section titles zh/hi/bo. "
    "'translit_full' is the 4-line romanized chant; 'uchen' and meaning.bo hold the Tibetan. "
    "FOR KHENPO REVIEW: (1) confirm Uchen spelling/stacking; (2) confirm the English realignment "
    "by one against the Tibetan; (3) CONFIRM whether the Root Praise repeats each round — for this "
    "proof of concept it is inside the repeat loop, but that is a guess pending review."),
  "languages": ["en","zh","hi","bo"],
  "review_flags": [
    "Root Praise currently repeats with the 21 each round (PoC assumption — khenpo to confirm).",
    "English-to-Tibetan alignment shifted by one so Tibetan numbering leads (khenpo to confirm).",
    "Uchen transcribed from pasted text, not verified glyph-by-glyph (khenpo to confirm)."
  ],
  "sequence": seq
}

with io.open("public/content.json","w",encoding="utf-8") as f:
    json.dump(content,f,ensure_ascii=False,indent=2)

# report
verses=[s for s in seq if s.get("type")=="verse"]
print("total steps:",len([s for s in seq if s['type'] in('section','verse')]))
print("verses:",len(verses),"(homage + root + 21 =",1+1+21,")")
print("loop covers:", "root + 21" )
print("sample praise-1 translit:", bo[1][1][0])
print("sample praise-1 english :", en_by_pdf_index[2][0])
