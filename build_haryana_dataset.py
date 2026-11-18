import json
import os

stands_data = [
    # Ambala
    {"name": "Ambala City", "district": "Ambala", "aliases": ["Ambala City Bus Stand", "Ambala", "Ambala Shehar"]},
    {"name": "Ambala Cantt", "district": "Ambala", "aliases": ["Ambala Cantt Bus Stand", "Ambala Cantonment", "Ambala Sadar"]},
    {"name": "Barara", "district": "Ambala", "aliases": ["Barara Bus Stand", "Barara Junction Stand"]},
    {"name": "Dosarka", "district": "Ambala", "aliases": ["Dosarka Bus Stand", "Dosarka Chowk"]},
    {"name": "Naraingarh", "district": "Ambala", "aliases": ["Naraingarh Bus Stand", "Narayan Garh"]},
    {"name": "Saha", "district": "Ambala", "aliases": ["Saha Bus Stand", "Saha Chowk"]},
    {"name": "Sehzadpur", "district": "Ambala", "aliases": ["Sehzadpur Bus Stand", "Shahzadpur"]},
    {"name": "Mullana", "district": "Ambala", "aliases": ["Mullana Town Stand", "Mullana Bus Stand"]},
    {"name": "MMDU Campus Gate", "district": "Ambala", "aliases": ["MMDU Gate", "MMDU Mullana", "Maharishi Markandeshwar University"]},

    # Bhiwani
    {"name": "Bhiwani", "district": "Bhiwani", "aliases": ["Bhiwani Bus Stand", "Bhiwani Junction"]},
    {"name": "Bawani Khera", "district": "Bhiwani", "aliases": ["Bawani Khera Bus Stand", "Bawanikhera"]},
    {"name": "Siwani", "district": "Bhiwani", "aliases": ["Siwani Bus Stand", "Siwani Mandi"]},
    {"name": "Tosham", "district": "Bhiwani", "aliases": ["Tosham Bus Stand", "Tosam"]},
    {"name": "Behal", "district": "Bhiwani", "aliases": ["Behal Bus Stand", "Bihal"]},
    {"name": "Bhadra", "district": "Bhiwani", "aliases": ["Bhadra Bus Stand", "Bhadra Border"]},
    {"name": "Dinod", "district": "Bhiwani", "aliases": ["Dinod Bus Stand", "Dinod Gate"]},
    {"name": "Chang", "district": "Bhiwani", "aliases": ["Chang Bus Stand", "Chang Mor"]},

    # Charkhi Dadri
    {"name": "Charkhi Dadri", "district": "Charkhi Dadri", "aliases": ["Charkhi Dadri Bus Stand", "Dadri"]},
    {"name": "Loharu", "district": "Charkhi Dadri", "aliases": ["Loharu Bus Stand", "Loharu Junction"]},
    {"name": "Badhra", "district": "Charkhi Dadri", "aliases": ["Badhra Bus Stand", "Badra"]},
    {"name": "Jhojhu Kalan", "district": "Charkhi Dadri", "aliases": ["Jhojhu Kalan Bus Stand", "Jhojhu"]},
    {"name": "Bond Kalan", "district": "Charkhi Dadri", "aliases": ["Bond Kalan Bus Stand", "Bond"]},

    # Faridabad
    {"name": "Faridabad", "district": "Faridabad", "aliases": ["Faridabad Bus Stand", "Old Faridabad Bus Stand"]},
    {"name": "Ballabhgarh", "district": "Faridabad", "aliases": ["Ballabhgarh Bus Stand", "Ballabgarh", "Raja Nahar Singh Stand"]},
    {"name": "NIT Faridabad", "district": "Faridabad", "aliases": ["NIT Faridabad Bus Stand", "Faridabad NIT", "Neelam Chowk"]},
    {"name": "Badkhal", "district": "Faridabad", "aliases": ["Badkhal Bus Stand", "Badkhal Mor"]},
    {"name": "Tigaon", "district": "Faridabad", "aliases": ["Tigaon Bus Stand", "Tigaon Mor"]},

    # Fatehabad
    {"name": "Fatehabad", "district": "Fatehabad", "aliases": ["Fatehabad Bus Stand"]},
    {"name": "Bhattu Kalan", "district": "Fatehabad", "aliases": ["Bhattu Kalan Bus Stand", "Bhattu Mandi"]},
    {"name": "Tohana", "district": "Fatehabad", "aliases": ["Tohana Bus Stand", "Tohana Sub-Depot"]},
    {"name": "Ratia", "district": "Fatehabad", "aliases": ["Ratia Bus Stand"]},
    {"name": "Jakhal", "district": "Fatehabad", "aliases": ["Jakhal Bus Stand", "Jakhal Mandi"]},
    {"name": "Bhuna", "district": "Fatehabad", "aliases": ["Bhuna Bus Stand", "Bhuna Mor"]},
    {"name": "Kullar", "district": "Fatehabad", "aliases": ["Kullar Bus Stand", "Kullar Mor"]},

    # Gurugram (Gurgaon)
    {"name": "Gurugram", "district": "Gurgaon", "aliases": ["Gurgaon", "Gurugram Bus Stand", "Gurgaon Old Bus Stand"]},
    {"name": "Pataudi", "district": "Gurgaon", "aliases": ["Patodi", "Pataudi Bus Stand", "Pataudi Road"]},
    {"name": "Sohna", "district": "Gurgaon", "aliases": ["Sohana", "Sohna Bus Stand", "Sohna Chowk"]},
    {"name": "Manesar", "district": "Gurgaon", "aliases": ["Manesar Bus Stand", "IMT Manesar"]},
    {"name": "Farrukhnagar", "district": "Gurgaon", "aliases": ["Farrukhnagar Bus Stand", "Farukh Nagar"]},
    {"name": "Badshahpur", "district": "Gurgaon", "aliases": ["Badshahpur Bus Stand", "Badshahpur Chowk"]},
    {"name": "IFFCO Chowk", "district": "Gurgaon", "aliases": ["IFFCO Chowk Stand", "IFFCO Chowk Bus Stop"]},
    {"name": "Rajiv Chowk Gurugram", "district": "Gurgaon", "aliases": ["Rajiv Chowk Gurgaon", "Rajiv Chowk Bus Stand"]},

    # Hisar
    {"name": "Hisar", "district": "Hisar", "aliases": ["Hisar Bus Stand", "Hissar", "Hisar Central Bus Stand"]},
    {"name": "Hisar Old Courts", "district": "Hisar", "aliases": ["Hisar Old Courts Stand", "Hisar Kachehri"]},
    {"name": "Hisar Cantt", "district": "Hisar", "aliases": ["Hisar Cantt Stand", "Hisar Military Station"]},
    {"name": "Barwala", "district": "Hisar", "aliases": ["Barwala Bus Stand", "Barwala Hisar"]},
    {"name": "Hansi", "district": "Hisar", "aliases": ["Hansi Bus Stand", "Hansi Sub-Depot"]},
    {"name": "Uklana", "district": "Hisar", "aliases": ["Uklana Bus Stand", "Uklana Mandi"]},
    {"name": "Adampur", "district": "Hisar", "aliases": ["Adampur Bus Stand", "Mandi Adampur"]},
    {"name": "Narnaund", "district": "Hisar", "aliases": ["Narnaund Bus Stand", "Narnaud"]},
    {"name": "Bass", "district": "Hisar", "aliases": ["Bass Bus Stand", "Bass Stand"]},
    {"name": "Agroha", "district": "Hisar", "aliases": ["Agroha Bus Stand", "Agroha Dham Stand"]},

    # Jind
    {"name": "Jind", "district": "Jind", "aliases": ["Jind Bus Stand", "Jind Junction Stand"]},
    {"name": "Narwana", "district": "Jind", "aliases": ["Narwana Bus Stand", "Narwana Sub-Depot"]},
    {"name": "Uchhana", "district": "Jind", "aliases": ["Uchhana Bus Stand", "Uchana"]},
    {"name": "Julana", "district": "Jind", "aliases": ["Julana Bus Stand", "Julana Mandi"]},
    {"name": "Safidon", "district": "Jind", "aliases": ["Safidon Bus Stand", "Safidon City"]},
    {"name": "Alewa", "district": "Jind", "aliases": ["Alewa Bus Stand"]},
    {"name": "Pillu Khera", "district": "Jind", "aliases": ["Pillu Khera Bus Stand", "Pillukhera"]},

    # Jhajjar
    {"name": "Jhajjar", "district": "Jhajjar", "aliases": ["Jhajjar Bus Stand"]},
    {"name": "Beri", "district": "Jhajjar", "aliases": ["Beri Bus Stand", "Beri Sub-Depot"]},
    {"name": "Bahadurgarh", "district": "Jhajjar", "aliases": ["Bahadurgarh Bus Stand", "Bahadurgarh City"]},
    {"name": "Badli", "district": "Jhajjar", "aliases": ["Badli Bus Stand", "Badli Chowk"]},
    {"name": "Matanhail", "district": "Jhajjar", "aliases": ["Matanhail Bus Stand"]},
    {"name": "Salhawas", "district": "Jhajjar", "aliases": ["Salhawas Bus Stand"]},

    # Kaithal
    {"name": "Kaithal", "district": "Kaithal", "aliases": ["Kaithal Bus Stand", "Kaithal City Stand"]},
    {"name": "Pundari", "district": "Kaithal", "aliases": ["Pundari Bus Stand", "Pundri"]},
    {"name": "Cheeka", "district": "Kaithal", "aliases": ["Cheeka Bus Stand", "Guhla Cheeka"]},
    {"name": "Pai", "district": "Kaithal", "aliases": ["Pai Bus Stand"]},
    {"name": "Rajond", "district": "Kaithal", "aliases": ["Rajond Bus Stand", "Rajound"]},
    {"name": "Dhand", "district": "Kaithal", "aliases": ["Dhand Bus Stand"]},
    {"name": "Kalayat", "district": "Kaithal", "aliases": ["Kalayat Bus Stand"]},
    {"name": "Koul", "district": "Kaithal", "aliases": ["Koul Bus Stand", "Kaul"]},
    {"name": "Siwan", "district": "Kaithal", "aliases": ["Siwan Bus Stand", "Seewan"]},

    # Karnal
    {"name": "Karnal", "district": "Karnal", "aliases": ["Karnal Bus Stand", "Old Karnal Bus Stand"]},
    {"name": "Karnal New", "district": "Karnal", "aliases": ["Karnal New Bus Stand", "Nirmal Kutiya Stand"]},
    {"name": "Gharaunda", "district": "Karnal", "aliases": ["Gharonda", "Gharaunda Bus Stand"]},
    {"name": "Indri", "district": "Karnal", "aliases": ["Indri Bus Stand"]},
    {"name": "Nilokheri", "district": "Karnal", "aliases": ["Nilokheri Bus Stand"]},
    {"name": "Taraori", "district": "Karnal", "aliases": ["Tarori", "Taraori Bus Stand"]},
    {"name": "Assandh", "district": "Karnal", "aliases": ["Ashandh", "Assandh Bus Stand"]},
    {"name": "Nissing", "district": "Karnal", "aliases": ["Nising", "Nissing Bus Stand"]},
    {"name": "Kunjpura", "district": "Karnal", "aliases": ["Kunjpura Bus Stand"]},

    # Kurukshetra
    {"name": "Kurukshetra", "district": "Kurukshetra", "aliases": ["Kurukshetra Bus Stand", "Kurukshetra University Stand"]},
    {"name": "Pipli", "district": "Kurukshetra", "aliases": ["Pipli Bus Stand", "Pipli Parshuram Chowk"]},
    {"name": "Pehowa", "district": "Kurukshetra", "aliases": ["Pehowa Bus Stand", "Pehwa"]},
    {"name": "Ladwa", "district": "Kurukshetra", "aliases": ["Ladwa Bus Stand"]},
    {"name": "Shahbad", "district": "Kurukshetra", "aliases": ["Shahbad Bus Stand", "Shahbad Markanda"]},
    {"name": "Thanesar", "district": "Kurukshetra", "aliases": ["Thanesar Bus Stand", "Thaneswar"]},
    {"name": "Babain", "district": "Kurukshetra", "aliases": ["Babain Bus Stand"]},
    {"name": "Ismailabad", "district": "Kurukshetra", "aliases": ["Ismailabad Bus Stand"]},
    {"name": "Jhansa", "district": "Kurukshetra", "aliases": ["Jhansa Bus Stand"]},

    # Mahendragarh (Mohindergarh)
    {"name": "Mohindergarh", "district": "Mohindergarh", "aliases": ["Mahendragarh", "Mohindergarh Bus Stand", "Mahendergarh"]},
    {"name": "Narnaul", "district": "Mohindergarh", "aliases": ["Narnaul Bus Stand", "Narnaul Sub-Depot"]},
    {"name": "Kanina", "district": "Mohindergarh", "aliases": ["Kanina Bus Stand", "Kanina Khas"]},
    {"name": "Ateli", "district": "Mohindergarh", "aliases": ["Ateli Bus Stand", "Ateli Mandi"]},
    {"name": "Nangal Chaudhry", "district": "Mohindergarh", "aliases": ["Nangal Chaudhry Bus Stand", "Nangal Chaudhary"]},
    {"name": "Satnali", "district": "Mohindergarh", "aliases": ["Satnali Bus Stand"]},

    # Panipat
    {"name": "Panipat", "district": "Panipat", "aliases": ["Panipat Bus Stand", "Panipat City Stand"]},
    {"name": "Israna", "district": "Panipat", "aliases": ["Israna Bus Stand"]},
    {"name": "Samalkha", "district": "Panipat", "aliases": ["Samalkha Bus Stand", "Samalkha GT Road"]},
    {"name": "Madlauda", "district": "Panipat", "aliases": ["Madlauda Bus Stand", "Matlauda"]},
    {"name": "Bapoli", "district": "Panipat", "aliases": ["Bapoli Bus Stand"]},

    # Panchkula
    {"name": "Panchkula", "district": "Panchkula", "aliases": ["Panchkula Bus Stand", "Panchkula Sector 5 Stand"]},
    {"name": "Chandigarh ISBT-17", "district": "Panchkula", "aliases": ["Chandigarh", "ISBT Sector 17", "Chandigarh 17"]},
    {"name": "Chandigarh ISBT-43", "district": "Panchkula", "aliases": ["ISBT Sector 43", "Chandigarh 43", "Chandigarh ISBT"]},
    {"name": "Kalka", "district": "Panchkula", "aliases": ["Kalka Bus Stand", "Kalka Station Stand"]},
    {"name": "Pinjore", "district": "Panchkula", "aliases": ["Pinjore Bus Stand", "Pinjore Gardens Stand"]},
    {"name": "Raipur Rani", "district": "Panchkula", "aliases": ["Raipur Rani Bus Stand"]},
    {"name": "Morni", "district": "Panchkula", "aliases": ["Morni Bus Stand", "Morni Hills Stand"]},

    # Rohtak
    {"name": "Rohtak", "district": "Rohtak", "aliases": ["Rohtak Bus Stand", "Rohtak New Bus Stand"]},
    {"name": "Meham", "district": "Rohtak", "aliases": ["Meham Bus Stand", "Maham"]},
    {"name": "Kalanaur (Rohtak)", "district": "Rohtak", "aliases": ["Kalanaur Rohtak Bus Stand", "Kalanaur"]},
    {"name": "Sampla", "district": "Rohtak", "aliases": ["Sampla Bus Stand", "Sampla Mor"]},
    {"name": "Lakhan Majra", "district": "Rohtak", "aliases": ["Lakhan Majra Bus Stand"]},

    # Rewari
    {"name": "Rewari", "district": "Rewari", "aliases": ["Rewari Bus Stand", "Rewari City Stand"]},
    {"name": "Bawal", "district": "Rewari", "aliases": ["Bawal Bus Stand", "Bawal HSIIDC"]},
    {"name": "Dharuhera", "district": "Rewari", "aliases": ["Dharuhera Bus Stand", "Dharuhera Chowk"]},
    {"name": "Kosali", "district": "Rewari", "aliases": ["Kosali Bus Stand", "Kosli"]},
    {"name": "Jatusana", "district": "Rewari", "aliases": ["Jatusana Bus Stand"]},
    {"name": "Kund", "district": "Rewari", "aliases": ["Kund Bus Stand", "Kund Barrier"]},

    # Sonipat
    {"name": "Sonipat", "district": "Sonipat", "aliases": ["Sonipat Bus Stand", "Sonepat"]},
    {"name": "Murthal", "district": "Sonipat", "aliases": ["Murthal Bus Stand", "Murthal Dhabas Stand"]},
    {"name": "Gohana", "district": "Sonipat", "aliases": ["Gohana Bus Stand", "Gohana Sub-Depot"]},
    {"name": "Ganaur", "district": "Sonipat", "aliases": ["Ganour", "Ganaur Bus Stand"]},
    {"name": "Kharkhoda", "district": "Sonipat", "aliases": ["Kharkhoda Bus Stand", "Kharkhauda"]},
    {"name": "Rai", "district": "Sonipat", "aliases": ["Rai Bus Stand", "Rai Sports School Stand"]},
    {"name": "Kundli", "district": "Sonipat", "aliases": ["Kundli Bus Stand", "Kundli Border"]},

    # Sirsa
    {"name": "Sirsa", "district": "Sirsa", "aliases": ["Sirsa Bus Stand", "Sirsa Central Stand"]},
    {"name": "Chautala", "district": "Sirsa", "aliases": ["Choutala", "Chautala Bus Stand"]},
    {"name": "Mandi Dabwali", "district": "Sirsa", "aliases": ["Dabwali", "Dabwali Bus Stand", "Mandi Dabwali Stand"]},
    {"name": "Ellenabad", "district": "Sirsa", "aliases": ["Ealanabad", "Ellenabad Bus Stand", "Ellanabad"]},
    {"name": "Rania", "district": "Sirsa", "aliases": ["Ranian", "Rania Bus Stand"]},
    {"name": "Kalanwali", "district": "Sirsa", "aliases": ["Kalawali", "Kalanwali Bus Stand", "Mandi Kalanwali"]},
    {"name": "Nathusari Chopta", "district": "Sirsa", "aliases": ["Chopta", "Nathusari Chopta Bus Stand"]},
    {"name": "Ding", "district": "Sirsa", "aliases": ["Ding Bus Stand", "Ding Mor"]},

    # Yamunanagar
    {"name": "Yamuna Nagar", "district": "Yamunanagar", "aliases": ["Yamunanagar", "Yamuna Nagar Bus Stand", "Yamuna Nagar Stand"]},
    {"name": "Jagadhri", "district": "Yamunanagar", "aliases": ["Jagadhari", "Jagadhri Bus Stand", "Jagadhri Stand"]},
    {"name": "Radaur", "district": "Yamunanagar", "aliases": ["Radaur Bus Stand"]},
    {"name": "Chhachhrauli", "district": "Yamunanagar", "aliases": ["Chachrouli", "Chhachhrauli Bus Stand"]},
    {"name": "Bilaspur", "district": "Yamunanagar", "aliases": ["Bilaspur Bus Stand", "Bilaspur Yamunanagar"]},
    {"name": "Sadhaura", "district": "Yamunanagar", "aliases": ["Sadhaura Bus Stand"]},
    {"name": "Mustafabad (Saraswati Nagar)", "district": "Yamunanagar", "aliases": ["Mustafabad Stand", "Saraswati Nagar", "Mustafabad Bus Stand"]},
    {"name": "Kalanaur Chowk", "district": "Yamunanagar", "aliases": ["Kalanaur Chowk Stand", "Kalanaur Highway Stand"]},

    # Mewat (Nuh)
    {"name": "Nuh", "district": "Mewat (Nuh)", "aliases": ["Nuh Bus Stand", "Mewat"]},
    {"name": "Ferozepur Jhirka", "district": "Mewat (Nuh)", "aliases": ["Firozpur Jhirka", "Ferozepur Jhirka Bus Stand"]},
    {"name": "Punhana", "district": "Mewat (Nuh)", "aliases": ["Punhana Bus Stand"]},
    {"name": "Taoru", "district": "Mewat (Nuh)", "aliases": ["Taoru Bus Stand", "Tauru"]},
    {"name": "Nagina", "district": "Mewat (Nuh)", "aliases": ["Nagina Bus Stand"]},

    # Palwal
    {"name": "Palwal", "district": "Palwal", "aliases": ["Palwal Bus Stand", "Palwal City"]},
    {"name": "Hodal", "district": "Palwal", "aliases": ["Hodal Bus Stand", "Hodal Border"]},
    {"name": "Hathin", "district": "Palwal", "aliases": ["Hathin Bus Stand"]},
    {"name": "Hassanpur", "district": "Palwal", "aliases": ["Hassanpur Bus Stand"]},
    {"name": "Alawalpur", "district": "Palwal", "aliases": ["Alawalpur Bus Stand", "Alawalpur Chowk"]}
]

os.makedirs('data', exist_ok=True)
with open('data/haryana_bus_stands.json', 'w', encoding='utf-8') as f:
    json.dump(stands_data, f, indent=2, ensure_ascii=False)

print(f"Successfully generated data/haryana_bus_stands.json with {len(stands_data)} stands.")
