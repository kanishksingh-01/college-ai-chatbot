# -*- coding: utf-8 -*-
"""
Multilingual Knowledge Base & Localized Natural Language Engine
GH Raisoni International Skill Tech University, Pune (Academic Year 2026-27)
Full high-fidelity support for Marathi (mr), Hindi (hi), and English (en).
"""

import math

MARATHI_KNOWLEDGE = {
    "Admission": (
        "🎓 **प्रवेश प्रक्रिया २०२६–२७ (जीएच रायसोनी स्किल टेक युनिव्हर्सिटी, पुणे)**\n\n"
        "• **पात्रता निकष**: १२वी (HSC) विज्ञान/वाणिज्य/कला किमान ४५% गुणांसह (मागासवर्गीय विद्यार्थ्यांसाठी ४०%) किंवा ३-वर्षीय इंजिनिअरिंग डिप्लोमा.\n"
        "• **प्रवेश पद्धत**: MHT-CET / JEE Main / PERA CET / थेट संस्थात्मक कोटा (Institute Level Seats).\n"
        "• **अर्ज कसा करावा**: अधिकृत पोर्टल `https://ghrcem.raisoni.net` वर ऑनलाइन नोंदणी करा किंवा वाघोली मुख्य कॅम्पस ॲडमिशन सेलला थेट भेट द्या.\n"
        "• **आवश्यक कागदपत्रे**: १०वी व १२वी गुणपत्रिका, शाळा सोडल्याचा दाखला (LC), जात व नॉन-क्रिमिलेअर प्रमाणपत्र, डोमिसाईल प्रमाणपत्र, आधार कार्ड आणि पासपोर्ट फोटो.\n"
        "• **मदत कक्ष संपर्क**: +९१ ९६०४७८४४४४ / ०२०-६७५२८००० (सकाळी ९:०० ते संध्याकाळी ५:३०)"
    ),
    "Fee Structure": (
        "💰 **फी रचना व भरणा माहिती (शैक्षणिक वर्ष २०२६–२७)**\n\n"
        "• **B.Tech / Engineering**: अंदाजे ₹१,४५,००० ते ₹१,६०,००० प्रति वर्ष\n"
        "• **BBA / BCA / Computer Applications**: अंदाजे ₹८५,००० ते ₹१,०५,००० प्रति वर्ष\n"
        "• **M.Tech / MBA**: अंदाजे ₹१,१५,००० प्रति वर्ष\n"
        "• **वसतिगृह फी (Hostel & Mess)**: ₹९५,००० ते ₹१,२५,००० प्रति वर्ष (पौष्टिक भोजन समाविष्ट)\n"
        "• **भरणा पद्धत**: ऑनलाइन विद्यार्थी ईआरपी पोर्टल, नेट बँकिंग/UPI, किंवा अकाउंट्स काउंटर ४ वर DD द्वारे.\n"
        "• **हप्ते (Installments)**: विशेष अर्जाद्वारे दोन हप्त्यांमध्ये भरण्याची सोय उपलब्ध आहे."
    ),
    "Exam Timetable": (
        "📅 **परीक्षा वेळापत्रक व नियम (Autonomous 2026–27)**\n\n"
        "• **मिड-सेमिस्टर परीक्षा (MSE)**: ऑक्टोबर/नोव्हेंबर २०२६\n"
        "• **अंतिम सत्र परीक्षा (ESE / End Sem)**: डिसेंबर २०२६ - जानेवारी २०२७\n"
        "• **हॉल तिकीट (Admit Card)**: परीक्षा सुरू होण्याच्या ७ दिवस आधी ईआरपी पोर्टलवरून डाउनलोड करता येईल.\n"
        "• **महत्त्वाचा नियम**: परीक्षेला बसण्यासाठी किमान **७५% हजेरी अनिवार्य** आहे. ७५% पेक्षा कमी हजेरी असल्यास विद्यार्थ्याला डिटेन्शन धोरणानुसार अतिरिक्त असाइनमेंट्स किंवा प्रिलिम्स द्यावे लागतील."
    ),
    "Attendance Rules": (
        "📊 **विद्यापीठ हजेरी नियम व डिटेन्शन धोरण (७५% नियम)**\n\n"
        "• **अनिवार्य नियम**: विद्यापीठाच्या नियमानुसार प्रत्येक विषयात किमान **७५% व्याख्यान हजेरी आवश्यक** आहे.\n"
        "• **७५% किंवा अधिक**: ✅ सुरक्षित - परीक्षेसाठी पूर्ण पात्र.\n"
        "• **६०% ते ७४.९% (इशारा वर्ग)**: मागील २ वर्षांच्या प्रश्नपत्रिका ओपन बुक पद्धतीने सोडवणे आवश्यक; अंतर्गत हजेरी गुण मिळणार नाहीत.\n"
        "• **५०% ते ५९.९% (गंभीर वर्ग)**: ओपन बुक पेपर्स + प्रिलिम परीक्षेत किमान ६०% गुण मिळवणे अनिवार्य.\n"
        "• **५०% पेक्षा कमी**: ❌ थेट डिटेन (No Consideration). सेमिस्टर परीक्षेत बसू दिले जाणार नाही.\n\n"
        "<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>"
    ),
    "Library Timings": (
        "📚 **केंद्रीय ग्रंथालय व वाचनालय (Central Library)**\n\n"
        "• **नियमित वेळ**: सकाळी ८:०० ते रात्री ८:०० (सोमवार ते शनिवार)\n"
        "• **परीक्षा काळातील वेळ**: २४x७ वाचन कक्ष खुला असतो.\n"
        "• **डिजिटल ग्रंथालय**: IEEE, ScienceDirect, Springer, NPTEL ई-बुक्सचा ऑनलाइन ॲक्सेस उपलब्ध.\n"
        "• **पुस्तक देवाणघेवाण**: एका वेळी ३ पुस्तके १५ दिवसांसाठी उपलब्ध.\n"
        "• **स्थान**: मुख्य इमारत, पहिला मजला (रूम १०५)."
    ),
    "Course Information": (
        "📖 **उपलब्ध पदवी व पदव्युत्तर अभ्यासक्रम**\n\n"
        "• **B.Tech**: AI & Data Science, Computer Science & Engineering, IT, Mechanical, Civil, E&TC.\n"
        "• **व्यवस्थापन व संगणक अनुप्रयोग**: BBA, BCA, MBA, MCA.\n"
        "• **वैशिष्ट्ये**: स्वायत्त (Autonomous) क्रेडिट सिस्टिम, हँड्स-ऑन इंडस्ट्री प्रोजेक्ट्स, इंटर्नशिप्स आणि कौशल्य प्रमाणपत्रे."
    ),
    "Faculty Contact": (
        "👨‍🏫 **प्राध्यापक व विभाग संपर्क**\n\n"
        "• **भेटण्याची वेळ**: दुपारी ३:३० ते संध्याकाळी ५:०० (किंवा पूर्वपरवानगीने).\n"
        "• **संगणक विभागप्रमुख (HOD)**: डॉ. ए. शर्मा (रूम २०१, दुसरा मजला).\n"
        "• **प्रकल्प मार्गदर्शक**: प्राध्यापिका शीला सातव (रूम २०३).\n"
        "• **मार्गदर्शक ईमेल**: `sheela.satav@raisoni.net`"
    ),
    "Branch Change": (
        "🔄 **शाखा बदल नियम (Branch Transfer)**\n\n"
        "• **पात्रता**: पहिल्या वर्षातील दोन्ही सेमिस्टर कोणत्याही बॅकलॉगशिवाय (All Clear) उत्तीर्ण.\n"
        "• **किमान पात्रता**: प्रथम वर्ष CGPA किमान ८.० किंवा त्याहून अधिक.\n"
        "• **अर्ज प्रक्रिया**: दुसऱ्या वर्षाच्या सेमिस्टर ३ सुरू होण्यापूर्वी ॲकॅडमिक सेलकडे विहित नमुन्यात अर्ज सादर करावा."
    ),
    "Placements": (
        "💼 **प्लेसमेंट व करिअर विकास कक्ष (Training & Placement)**\n\n"
        "• **सर्वोच्च पॅकेज**: ₹४५ LPA (आंतरराष्ट्रीय/उत्कृष्ट)\n"
        "• **सरासरी पॅकेज**: ₹५.५ ते ७.२ LPA\n"
        "• **प्रमुख कंपन्या**: TCS, Infosys, Wipro, Capgemini, Tech Mahindra, Cognizant, Amazon, Jio, Persistent Systems.\n"
        "• **प्लेसमेंट सेल स्थान**: ॲडमिन बिल्डिंग, दुसरा मजला, रूम २०२.\n"
        "• **प्रशिक्षण**: संवाद कौशल्य, ॲप्टिट्यूड आणि कोडिंग चाचण्यांचे विशेष प्रशिक्षण दिले जाते."
    ),
    "Hostel & Mess": (
        "🏢 **वसतिगृह (Hostel) व मेस सुविधा**\n\n"
        "• **खोल्यांचे प्रकार**: २/३ सीटर खोल्या (वायफाय, स्वतंत्र अभ्यास टेबल, कपाट).\n"
        "• **मेस सुविधा**: शुद्ध शाकाहारी व पौष्टिक नाश्ता, दुपारचे व रात्रीचे जेवण (अमर्यादित थाळी).\n"
        "• **सुरक्षा**: २४x७ बायोमेट्रिक प्रवेश, सीसीटीव्ही आणि सुरक्षा रक्षक.\n"
        "• **फी**: ₹९५,००० ते ₹१,२५,००० प्रति वर्ष (भोजन समाविष्ट)."
    ),
    "Scholarships": (
        "🏅 **शासकीय व संस्थात्मक शिष्यवृत्ती (Scholarships)**\n\n"
        "• **महाडीबीटी (MahaDBT)**: SC/ST/VJNT/OBC/SBC प्रवर्गासाठी १००% व ५०% फी सवलत.\n"
        "• **ईबीसी (EBC) सवलत**: खुल्या प्रवर्गातील आर्थिक दुर्बल घटकांसाठी ५०% ट्युशन फी सवलत.\n"
        "• **गुणवत्ता शिष्यवृत्ती**: MHT-CET/JEE मध्ये ९०% पेक्षा जास्त गुण मिळवणाऱ्या विद्यार्थ्यांना विशेष संस्थात्मक सवलत."
    ),
    "Clubs & Extracurriculars": (
        "🎨 **विद्यार्थी क्लब्स व सांस्कृतिक उपक्रम**\n\n"
        "• **तांत्रिक क्लब्स**: Coding Club, AI & Robotics Club, Google Developer Student Club (GDSC).\n"
        "• **सांस्कृतिक व क्रीडा**: 'अंतरांग' वार्षिक स्नेहसंमेलन, क्रिकेट, फुटबॉल, बॅडमिंटन कोर्ट्स.\n"
        "• **सामाजिक उपक्रम**: राष्ट्रीय सेवा योजना (NSS), रोटरॅक्ट क्लब, रक्तदान शिबिरे."
    ),
    "Emergency & Helpline": (
        "🚨 **आपत्कालीन संपर्क व सुरक्षा क्रमांक**\n\n"
        "• **कॅम्पस सुरक्षा कक्ष**: +९१ २०-६७५२८००० / +९१ ९६०४७८४४४४\n"
        "• **वैद्यकीय ओपीडी (Medical Center)**: तळमजला, रूम ०५ (डॉक्टर उपलब्ध)\n"
        "• **महिला तक्रार निवारण (ICC)**: +९१ ९८२२४४५५६६\n"
        "• **ॲम्ब्युलन्स**: १०८ / ०२०-६७५२८१००\n"
        "• **रॅगिंग विरोधी हेल्पलाईन**: १८००-१८०-५५२२ (टोल फ्री)\n\n"
        "<button class='action-pill-btn' onclick='openSosModal()'>🆘 तातडीची मदत (SOS)</button>"
    ),
    "Campus Location & Map": (
        "📍 **कॅम्पस पत्ता व स्थान**\n\n"
        "• **मुख्य परिसर**: जीएच रायसोनी स्किल टेक युनिव्हर्सिटी, पुणे-नगर रोड, वाघोली, पुणे - ४१२२०७.\n"
        "• **जवळचे बस स्थानक**: वाघोली बाझार / रायसोनी कॉलेज पीएमपीएमएल थांबा (१०० मीटर).\n"
        "• **पुणे रेल्वे स्टेशनपासून अंतर**: १४ किमी.\n"
        "• **पुणे विमानतळापासून अंतर**: ९ किमी."
    ),
    "Canteen & Mess Menu": (
        "🍛 **कॅम्पस कॅन्टीन व मेस सुविधा**\n\n"
        "• **कॅन्टीन वेळ**: सकाळी ८:०० ते रात्री ८:३०\n"
        "• **दुपारचे जेवण**: दुपारी १२:०० ते २:३० (अमर्यादित थाळी ₹७० - ₹९०)\n"
        "• **नाश्ता पर्याय**: पोहे, उपमा, इडली सांबार, वडा पाव, मिसळ पाव, चहा आणि कॉफी.\n"
        "• **मेस पद्धत**: मासिक कूपन किंवा प्रति थाळी पेमेंट उपलब्ध.\n"
        "• **स्थान**: सेंट्रल ग्राउंड्सजवळ, हॉस्टेल ब्लॉक समोर."
    ),
    "Campus Floor & Room Locator": (
        "🗺️ **कॅम्पस मजला व कक्ष शोधक (वाघोली मुख्य इमारत)**\n\n"
        "• **तळमजला (Ground Floor)**: सेंट्रल रिसेप्शन, ॲडमिशन सेल, अकाउंट्स काउंटर ४, विद्यार्थी सुविधा केंद्र.\n"
        "• **पहिला मजला (1st Floor)**: कॉम्प्युटर सायन्स लॅब्स (१०१-१०८), डेटा सायन्स सेंटर, लायब्ररी.\n"
        "• **दुसरा मजला (2nd Floor)**: AI इनोव्हेशन लॅब, ट्रेनिंग आणि प्लेसमेंट सेल (रूम २०२).\n"
        "• **तिसरा मजला (3rd Floor)**: क्लासरूम्स ३०१-३२०, इलेक्ट्रॉनिक्स लॅब, सेमिनार हॉल.\n"
        "• **चौथा मजला (4th Floor)**: मुख्य ऑडिटोरियम, संशोधन केंद्र, एक्झामिनेशन सेल.\n\n"
        "<button class='action-pill-btn' onclick='openMapModal()'>🗺️ फ्लोअर नकाशा उघडा</button>"
    ),
    "Bonafide & Document Services": (
        "📄 **बोनाफाइड प्रमाणपत्र व दस्तऐवज सेवा**\n\n"
        "• **उपलब्ध सेवा**: बोनाफाइड प्रमाणपत्र, बस/रेल्वे सवलत पास (Concession Pass), फी कोटेशन, एनओसी (NOC).\n"
        "• **डिजिटल अर्ज**: खाली दिलेल्या बटणावर क्लिक करून त्वरित डिजिटल प्रत पहा आणि प्रिंट करा:\n\n"
        "<button class='action-pill-btn' onclick='openBonafideModal()'>📄 बोनाफाइड प्रमाणपत्र उघडा</button>"
    ),
    "Attendance & Bunk Calculator Guide": (
        "🎯 **बंक कॅल्क्युलेटर व हजेरी नियम मार्गदर्शक**\n\n"
        "• **७५% नियम**: प्रत्येक विषयात किमान ७५% व्याख्यान हजेरी आवश्यक आहे.\n"
        "• **बंक सूत्र**: `सुरक्षित बंक = (उपस्थित तास / ०.७५) - एकूण घेतलेले तास`\n"
        "• **डिटेन्शन रिकव्हरी**: ७५% पेक्षा कमी हजेरी असल्यास डिटेन न होण्यासाठी सलग १००% उपस्थिती आवश्यक असते.\n\n"
        "<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>"
    ),
    "Campus Amenities & WiFi": (
        "📶 **कॅम्पस सुविधा व हाय-स्पीड वायफाय**\n\n"
        "• **वायफाय नाव (SSID)**: `GHR-Campus-5G` आणि `GHR-Student-WiFi`\n"
        "• **लॉगिन पद्धत**: तुमचा पीआरएन (उदा. `ISTU00000001`) आणि ईआरपी पासवर्ड वापरा.\n"
        "• **पार्किंग**: दुचाकी व चारचाकी वाहनांसाठी प्रवेशद्वाराजवळ विनामूल्य पार्किंग झोन (विद्यार्थी ओळखपत्र आवश्यक).\n"
        "• **झेरॉक्स व प्रिंटिंग सेंटर**: तळमजला, लायब्ररी शेजारी (सकाळी ८:३० ते संध्याकाळी ६:००)."
    ),
    "Academic Regulations & Grading": (
        "📊 **शैक्षणिक नियम व ग्रेडिंग सिस्टिम (१०-पॉइंट स्केल)**\n\n"
        "• **उत्तीर्ण निकष**: प्रत्येक विषयात थिअरी व प्रॅक्टिकलमध्ये किमान **४०% गुण आवश्यक** (MSE, ESE व अंतर्गत गुण मिळून).\n"
        "• **ग्रेडिंग स्केल**: O (९०+), A+ (८०-८९), A (७०-७९), B+ (६०-६९), B (५५-५९), C (५०-५४), P (४०-४९), F (<४० नापास).\n"
        "• **ATKT नियम**: पुढील वर्षात जाण्यासाठी जास्तीत जास्त ४ बॅकलॉग विषयांमधील अनुशेष चालतो."
    ),
    "University Leadership & Faculty": (
        "🏛️ **विद्यापीठ नेतृत्व व प्रशासन**\n\n"
        "• **कुलगुरु (Vice Chancellor)**: **डॉ. आर. डी. खराडकर**\n"
        "• **प्रकल्प मार्गदर्शक (Project Guide)**: **सहाय्यक प्राध्यापिका शीला सातव** (Asst. Prof. Sheela Satav)\n"
        "• **विभागप्रमुख (HOD)**: **डॉ. ए. शर्मा** (संगणक विभाग)\n"
        "• **कॅम्पस**: वाघोली मुख्य परिसर, पुणे"
    ),
    "Academic Calendar & Holidays": (
        "🗓️ **शैक्षणिक दिनदर्शिका २०२६–२७ (सुट्ट्या व कार्यक्रम)**\n\n"
        "• **सत्र सुरू**: जुलै २०२६\n"
        "• **गणेशोत्सव सुट्टी**: सप्टेंबर २०२६\n"
        "• **दिवाळी सुट्टी**: ऑक्टोबर/नोव्हेंबर २०२६\n"
        "• **सेमिस्टर परीक्षा**: डिसेंबर २०२६ - जानेवारी २०२७\n"
        "• **वार्षिक स्नेहसंमेलन 'अंतरांग'**: फेब्रुवारी २०२७"
    ),
    "Student Life & Chatbot Info": (
        "🤖 **जीएच रायसोनी कॉलेज एआय कॅम्पस असिस्टंट**\n\n"
        "• **विकसक**: **कनिष्क सिंग** (Kanishk Singh) आणि प्रकल्प चमू\n"
        "• **मार्गदर्शक**: **प्राध्यापिका शीला सातव**\n"
        "• **वैशिष्ट्ये**: २४/७ शैक्षणिक प्रश्न, बंक सिम्युलेटर, ३D डिजिटल ओळखपत्र, बोनाफाइड जनरेटर आणि कॅम्पस नेव्हिगेशन."
    )
}

HINDI_KNOWLEDGE = {
    "Admission": (
        "🎓 **प्रवेश प्रक्रिया 2026–27 (जीएच रायसोनी स्किल टेक यूनिवर्सिटी, पुणे)**\n\n"
        "• **पात्रता मानदंड**: 12वीं (HSC) विज्ञान/वाणिज्य/कला में न्यूनतम 45% अंक (आरक्षित वर्ग हेतु 40%) या 3-वर्षीय इंजीनियरिंग डिप्लोमा।\n"
        "• **प्रवेश माध्यम**: MHT-CET / JEE Main / PERA CET / सीधे संस्थागत कोटा (Institute Level Seats)।\n"
        "• **आवेदन कैसे करें**: आधिकारिक पोर्टल `https://ghrcem.raisoni.net` पर ऑनलाइन पंजीकरण करें या वाघोली मुख्य परिसर में प्रवेश सेल से संपर्क करें।\n"
        "• **आवश्यक दस्तावेज**: 10वीं व 12वीं की मार्कशीट, टीसी/एलसी, जाति प्रमाण पत्र, अधिवास (डोमिसाइल) प्रमाण पत्र, आधार कार्ड और पासपोर्ट साइज फोटो।\n"
        "• **हेल्पलाइन नंबर**: +91 9604784444 / 020-67528000 (प्रातः 9:00 से सायं 5:30 तक)"
    ),
    "Fee Structure": (
        "💰 **फीस संरचना एवं भुगतान विवरण (शैक्षणिक सत्र 2026–27)**\n\n"
        "• **B.Tech / Engineering**: लगभग ₹1,45,000 से ₹1,60,000 प्रति वर्ष\n"
        "• **BBA / BCA / Computer Applications**: लगभग ₹85,000 से ₹1,05,000 प्रति वर्ष\n"
        "• **M.Tech / MBA**: लगभग ₹1,15,000 प्रति वर्ष\n"
        "• **छात्रावास फीस (Hostel & Mess)**: ₹95,000 से ₹1,25,000 प्रति वर्ष (भोजन सहित)\n"
        "• **भुगतान विधि**: ऑनलाइन छात्र ईआरपी पोर्टल, नेट बैंकिंग/UPI, या अकाउंट्स काउंटर 4 पर डीडी द्वारा।\n"
        "• **किस्तें (Installments)**: विशेष अनुमति से दो किस्तों में भुगतान की सुविधा उपलब्ध है।"
    ),
    "Exam Timetable": (
        "📅 **परीक्षा समय सारणी व नियम (Autonomous 2026–27)**\n\n"
        "• **मिड-सेमेस्टर परीक्षा (MSE)**: अक्टूबर/नवंबर 2026\n"
        "• **सत्रांत परीक्षा (ESE / End Sem)**: दिसंबर 2026 - जनवरी 2027\n"
        "• **प्रवेश पत्र (Admit Card)**: परीक्षा प्रारंभ होने से 7 दिन पूर्व ईआरपी पोर्टल से डाउनलोड किया जा सकता है।\n"
        "• **अनिवार्य नियम**: परीक्षा में बैठने हेतु न्यूनतम **75% उपस्थिति अनिवार्य** है।"
    ),
    "Attendance Rules": (
        "📊 **विश्वविद्यालय उपस्थिति नियम व डिटेंशन नीति (75% नियम)**\n\n"
        "• **अनिवार्य नियम**: प्रत्येक विषय में न्यूनतम **75% व्याख्यान उपस्थिति अनिवार्य** है।\n"
        "• **75% या अधिक**: ✅ सुरक्षित - परीक्षा हेतु पूर्णतः पात्र।\n"
        "• **60% से 74.9% (चेतावनी)**: पूर्व 2 वर्षों के प्रश्न पत्र ओपन बुक पद्धति से हल करना अनिवार्य; आंतरिक उपस्थिति अंक नहीं मिलेंगे।\n"
        "• **50% से 59.9% (गंभीर स्थिति)**: ओपन बुक पेपर्स + प्रीलिम परीक्षा में न्यूनतम 60% अंक प्राप्त करना आवश्यक।\n"
        "• **50% से कम**: ❌ सीधे डिटेन (No Consideration)। सेमेस्टर परीक्षा में बैठने की अनुमति नहीं होगी।\n\n"
        "<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>"
    ),
    "Library Timings": (
        "📚 **केंद्रीय पुस्तकालय (Central Library)**\n\n"
        "• **सामान्य समय**: प्रातः 8:00 से सायं 8:00 बजे तक (सोमवार से शनिवार)\n"
        "• **परीक्षा अवधि**: 24x7 अध्ययन कक्ष खुला रहता है।\n"
        "• **डिजिटल लाइब्रेरी**: IEEE, ScienceDirect, Springer, NPTEL ई-बुक्स का ऑनलाइन एक्सेस उपलब्ध।\n"
        "• **स्थान**: मुख्य भवन, प्रथम तल (कमरा 105)।"
    ),
    "Course Information": (
        "📖 **उपलब्ध पाठ्यक्रम (डिग्री व स्नातकोत्तर)**\n\n"
        "• **B.Tech**: AI & Data Science, Computer Science & Engineering, IT, Mechanical, Civil, E&TC.\n"
        "• **प्रबंधन व कंप्यूटर अनुप्रयोग**: BBA, BCA, MBA, MCA.\n"
        "• **विशेषताएं**: स्वायत्त (Autonomous) क्रेडिट प्रणाली, हैंड्स-ऑन इंडस्ट्री प्रोजेक्ट्स एवं इंटर्नशिप।"
    ),
    "Faculty Contact": (
        "👨‍🏫 **शिक्षक व विभाग संपर्क**\n\n"
        "• **मिलने का समय**: दोपहर 3:30 से सायं 5:00 बजे तक।\n"
        "• **कंप्यूटर विभागाध्यक्ष (HOD)**: डॉ. ए. शर्मा (कमरा 201, द्वितीय तल)।\n"
        "• **परियोजना मार्गदर्शक**: प्रो. शीला सातव (कमरा 203)।\n"
        "• **ईमेल**: `sheela.satav@raisoni.net`"
    ),
    "Branch Change": (
        "🔄 **शाखा परिवर्तन नियम (Branch Change)**\n\n"
        "• **पात्रता**: प्रथम वर्ष के दोनों सेमेस्टर बिना किसी बैकलॉग (All Clear) के उत्तीर्ण।\n"
        "• **न्यूनतम CGPA**: प्रथम वर्ष में 8.0 या उससे अधिक CGPA आवश्यक।\n"
        "• **प्रक्रिया**: द्वितीय वर्ष प्रारंभ होने से पूर्व अकादमिक सेल में आवेदन पत्र जमा करें।"
    ),
    "Placements": (
        "💼 **प्रशिक्षण व प्लेसमेंट सेल (Training & Placement)**\n\n"
        "• **उच्चतम पैकेज**: ₹45 LPA (अंतर्राष्ट्रीय/उत्कृष्ट)\n"
        "• **औसत पैकेज**: ₹5.5 से 7.2 LPA\n"
        "• **प्रमुख भर्तीकर्ता**: TCS, Infosys, Wipro, Capgemini, Tech Mahindra, Cognizant, Amazon, Jio, Persistent Systems.\n"
        "• **स्थान**: एडमिन बिल्डिंग, द्वितीय तल, कमरा 202।"
    ),
    "Hostel & Mess": (
        "🏢 **छात्रावास (Hostel) व मेस सुविधाएं**\n\n"
        "• **कमरे**: 2/3 सीटर कमरे (वाई-फाई, व्यक्तिगत स्टडी टेबल, अलमारी)।\n"
        "• **मेस**: शुद्ध शाकाहारी व पौष्टिक नाश्ता, दोपहर व रात्रि भोजन (असीमित थाली)।\n"
        "• **सुरक्षा**: 24x7 बायोमेट्रिक प्रवेश, सीसीटीवी और गार्ड्स।\n"
        "• **शुल्क**: ₹95,000 से ₹1,25,000 प्रति वर्ष (भोजन सहित)।"
    ),
    "Scholarships": (
        "🏅 **छात्रवृत्ति विवरण (Scholarships)**\n\n"
        "• **महाडीबीटी (MahaDBT)**: SC/ST/VJNT/OBC/SBC श्रेणियों हेतु 100% व 50% फीस छूट।\n"
        "• **ईबीसी (EBC) छूट**: सामान्य वर्ग के आर्थिक रूप से कमजोर छात्रों हेतु 50% ट्यूशन फीस छूट।\n"
        "• **मेरिट छात्रवृत्ति**: प्रवेश परीक्षाओं में 90%+ अंक वाले छात्रों हेतु विशेष संस्थागत छूट।"
    ),
    "Clubs & Extracurriculars": (
        "🎨 **छात्र क्लब व गतिविधियां**\n\n"
        "• **तकनीकी क्लब**: Coding Club, AI & Robotics Club, GDSC (Google Developer Student Club)।\n"
        "• **सांस्कृतिक व खेल**: वार्षिक उत्सव 'अंतरंग', क्रिकेट, फुटबॉल, बैडमिंटन कोर्ट्स।\n"
        "• **सामाजिक पहल**: राष्ट्रीय सेवा योजना (NSS), रोटरैक्ट क्लब।"
    ),
    "Emergency & Helpline": (
        "🚨 **आपातकालीन संपर्क व सुरक्षा नंबर**\n\n"
        "• **परिसर सुरक्षा हेल्पलाइन**: +91 20-67528000 / +91 9604784444\n"
        "• **चिकित्सा केंद्र (OPD)**: ग्राउंड फ्लोर, कमरा 05 (डॉक्टर उपस्थित)\n"
        "• **महिला शिकायत निवारण (ICC)**: +91 9822445566\n"
        "• **एम्बुलेंस**: 108 / 020-67528100\n"
        "• **एंटी-रैगिंग हेल्पलाइन**: 1800-180-5522 (टोल फ्री)\n\n"
        "<button class='action-pill-btn' onclick='openSosModal()'>🆘 आपातकालीन सहायता (SOS)</button>"
    ),
    "Campus Location & Map": (
        "📍 **परिसर का पता एवं स्थान**\n\n"
        "• **मुख्य परिसर**: जीएच रायसोनी स्किल टेक यूनिवर्सिटी, पुणे-नगर रोड, वाघोली, पुणे - 412207।\n"
        "• **निकटतम बस स्टैंड**: वाघोली बाज़ार / रायसोनी कॉलेज पीएमपीएमएल स्टॉप (100 मीटर)।\n"
        "• **पुणे रेलवे स्टेशन से दूरी**: 14 किमी।\n"
        "• **पुणे हवाई अड्डे से दूरी**: 9 किमी।"
    ),
    "Canteen & Mess Menu": (
        "🍛 **कैंटीन व मेस सुविधाएं**\n\n"
        "• **कैंटीन समय**: प्रातः 8:00 से सायं 8:30 तक\n"
        "• **दोपहर का भोजन**: दोपहर 12:00 से 2:30 बजे तक (असीमित थाली ₹70 - ₹90)\n"
        "• **नाश्ता**: पोहा, उपमा, इडली सांबर, वड़ा पाव, मिसल पाव, चाय व कॉफी।\n"
        "• **स्थान**: सेंट्रल ग्राउंड्स के समीप, हॉस्टल ब्लॉक के सामने।"
    ),
    "Campus Floor & Room Locator": (
        "🗺️ **परिसर मंजिल व कक्ष खोजक (वाघोली मुख्य भवन)**\n\n"
        "• **भूतल (Ground Floor)**: सेंट्रल रिसेप्शन, प्रवेश सेल, अकाउंट्स काउंटर 4, छात्र सुविधा केंद्र।\n"
        "• **प्रथम तल (1st Floor)**: कंप्यूटर साइंस लैब्स (101-108), डेटा साइंस सेंटर, लाइब्रेरी।\n"
        "• **द्वितीय तल (2nd Floor)**: AI इनोवेशन लैब, ट्रेनिंग एवं प्लेसमेंट सेल (कमरा 202)।\n"
        "• **तृतीय तल (3rd Floor)**: क्लासरूम्स 301-320, इलेक्ट्रॉनिक्स लैब, सेमिनार हॉल।\n"
        "• **चतुर्थ तल (4th Floor)**: मुख्य ऑडिटोरियम, रिसर्च सेंटर, परीक्षा सेल।\n\n"
        "<button class='action-pill-btn' onclick='openMapModal()'>🗺️ फ्लोर नक्शा खोलें</button>"
    ),
    "Bonafide & Document Services": (
        "📄 **बोनाफाइड प्रमाण पत्र व दस्तावेज सेवाएं**\n\n"
        "• **उपलब्ध सेवाएं**: बोनाफाइड प्रमाण पत्र, बस/रेलवे कंसेशन पास, फीस कोटेशन, एनओसी (NOC)।\n"
        "• **डिजिटल आवेदन**: नीचे दिए गए बटन पर क्लिक कर तुरंत डिजिटल प्रति देखें और प्रिंट करें:\n\n"
        "<button class='action-pill-btn' onclick='openBonafideModal()'>📄 बोनाफाइड प्रमाण पत्र खोलें</button>"
    ),
    "Attendance & Bunk Calculator Guide": (
        "🎯 **बंक कैलकुलेटर व उपस्थिति गाइड**\n\n"
        "• **75% नियम**: प्रत्येक विषय में कम से कम 75% उपस्थिति आवश्यक है।\n"
        "• **बंक सूत्र**: `सुरक्षित बंक = (उपस्थित कक्षाएं / 0.75) - कुल कक्षाएं`\n"
        "• **डिटेंशन रिकवरी**: 75% से कम होने पर डिटेन होने से बचने हेतु लगातार 100% उपस्थिति अनिवार्य होती है।\n\n"
        "<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>"
    ),
    "Campus Amenities & WiFi": (
        "📶 **परिसर सुविधाएं व हाई-स्पीड वाई-फाई**\n\n"
        "• **वाई-फाई नाम (SSID)**: `GHR-Campus-5G` एवं `GHR-Student-WiFi`\n"
        "• **लॉगिन विधि**: अपना पीआरएन (उदा. `ISTU00000001`) और ईआरपी पासवर्ड उपयोग करें।\n"
        "• **पार्किंग**: दोपहिया और चार पहिया वाहनों हेतु मुख्य द्वार के पास निःशुल्क पार्किंग (आईडी कार्ड आवश्यक)।\n"
        "• **ज़ेरॉक्स सेंटर**: भूतल, लाइब्रेरी के बगल में (प्रातः 8:30 से सायं 6:00 बजे तक)।"
    ),
    "Academic Regulations & Grading": (
        "📊 **अकादमिक नियम व ग्रेडिंग प्रणाली (10-पॉइंट स्केल)**\n\n"
        "• **उत्तीर्ण अंक**: प्रत्येक विषय में थ्योरी व प्रैक्टिकल में न्यूनतम **40% अंक आवश्यक** (MSE, ESE व आंतरिक अंक मिलाकर)।\n"
        "• **ग्रेडिंग स्केल**: O (90+), A+ (80-89), A (70-79), B+ (60-69), B (55-59), C (50-54), P (40-49), F (<40 अनुत्तीर्ण)।\n"
        "• **ATKT नियम**: अगले वर्ष में प्रवेश हेतु अधिकतम 4 बैकलॉग विषयों की अनुमति है।"
    ),
    "University Leadership & Faculty": (
        "🏛️ **विश्वविद्यालय नेतृत्व व प्रशासन**\n\n"
        "• **कुलपति (Vice Chancellor)**: **डॉ. आर. डी. खराडकर**\n"
        "• **परियोजना मार्गदर्शक (Project Guide)**: **सहायक प्राध्यापिका शीला सातव** (Asst. Prof. Sheela Satav)\n"
        "• **विभागाध्यक्ष (HOD)**: **डॉ. ए. शर्मा** (कंप्यूटर विभाग)\n"
        "• **परिसर**: वाघोली मुख्य परिसर, पुणे"
    ),
    "Academic Calendar & Holidays": (
        "🗓️ **अकादमिक कैलेंडर 2026–27 (अवकाश व कार्यक्रम)**\n\n"
        "• **सत्र प्रारंभ**: जुलाई 2026\n"
        "• **गणेशोत्सव अवकाश**: सितंबर 2026\n"
        "• **दीपावली अवकाश**: अक्टूबर/नवंबर 2026\n"
        "• **सेमेस्टर परीक्षाएं**: दिसंबर 2026 - जनवरी 2027\n"
        "• **वार्षिक उत्सव 'अंतरंग'**: फरवरी 2027"
    ),
    "Student Life & Chatbot Info": (
        "🤖 **जीएच रायसोनी कॉलेज एआई कैंपस सहायक**\n\n"
        "• **डेवलपर**: **कनिष्क सिंह** (Kanishk Singh) एवं प्रोजेक्ट टीम\n"
        "• **मार्गदर्शक**: **प्रो. शीला सातव**\n"
        "• **विशेषताएं**: 24/7 अकादमिक सहायता, बंक सिम्युलेटर, 3D डिजिटल पहचान पत्र, बोनाफाइड जनरेटर व परिसर नेविगेशन।"
    )
}

# Cross-language synonym mapping for Marathi and Hindi queries
CROSS_LANG_SYNONYMS = {
    # Marathi
    "हजेरी": ["attendance", "hazari", "hajeri"],
    "उपस्थिती": ["attendance", "present"],
    "बंक": ["bunk", "leave", "chutti", "miss"],
    "तास": ["class", "lecture", "period"],
    "वर्ग": ["class", "classroom"],
    "फी": ["fee", "fees", "shulk"],
    "शुल्क": ["fee", "fees", "shulk"],
    "परीक्षा": ["exam", "examination", "timetable"],
    "वेळापत्रक": ["timetable", "schedule"],
    "प्रवेश": ["admission", "admissions", "seat"],
    "वसतिगृह": ["hostel", "mess"],
    "मेस": ["mess", "canteen", "food"],
    "कॅन्टीन": ["canteen", "mess", "food"],
    "नकाशा": ["map", "location", "floor"],
    "मजला": ["floor", "room"],
    "बोनाफाइड": ["bonafide", "certificate"],
    "प्रमाणपत्र": ["bonafide", "certificate"],
    "आयडी": ["id", "card", "pass"],
    "ओळखपत्र": ["id", "identity", "card"],
    "मार्गदर्शक": ["mentor", "guide"],
    "ग्रंथालय": ["library", "books"],
    "वाचनालय": ["library", "reading"],
    "शिष्यवृत्ती": ["scholarship", "scholarships"],
    "प्लेसमेंट": ["placement", "placements", "job"],
    "वायफाय": ["wifi", "internet"],
    "पार्किंग": ["parking", "vehicle"],
    "गुण": ["marks", "cgpa", "score"],
    "निकाल": ["result", "marks", "grade"],
    "सुट्टी": ["holiday", "calendar", "leave"],
    "सुट्ट्या": ["holiday", "calendar"],
    
    # Hindi
    "उपस्थिति": ["attendance", "present"],
    "हाजिरी": ["attendance", "hazari"],
    "कक्षा": ["class", "lecture"],
    "कक्षाएं": ["classes", "lectures"],
    "फीस": ["fee", "fees", "shulk"],
    "समयसारणी": ["timetable", "schedule"],
    "छात्रावास": ["hostel", "mess"],
    "कैंटीन": ["canteen", "mess", "food"],
    "नक्शा": ["map", "location", "floor"],
    "मंजिल": ["floor", "room"],
    "पहचानपत्र": ["id", "card", "pass"],
    "पुस्तकालय": ["library", "books"],
    "छात्रवृत्ति": ["scholarship", "scholarships"],
    "नौकरी": ["placement", "placements", "job"],
    "छुट्टी": ["holiday", "calendar", "leave"],
    "छुट्टियां": ["holiday", "calendar"]
}


def get_localized_answer(category, default_answer, lang="en"):
    """Returns category answer in user's preferred language."""
    if lang == "mr" and category in MARATHI_KNOWLEDGE:
        return MARATHI_KNOWLEDGE[category]
    elif lang == "hi" and category in HINDI_KNOWLEDGE:
        return HINDI_KNOWLEDGE[category]
    return default_answer


def get_localized_fallback(message, student=None, lang="en"):
    """Returns helpful assistant fallback in user's preferred language."""
    name_str = f" {student['name'].split()[0]}" if student else ""

    if lang == "mr":
        return (
            f"मला *\"{message}\"* या प्रश्नासाठी थेट उत्तर सापडले नाही.\n\n"
            f"अधिकृत **जीएच रायसोनी कॉलेज स्मार्ट असिस्टंट** म्हणून मी खालील गोष्टींमध्ये थेट मदत करू शकतो:\n"
            f"• 🎯 **हजेरी व बंक सिम्युलेटर**: विचारा *'मी आज २ तास गैरहजर राहिलो तर?'* किंवा *'मी बंक करू शकतो का?'*\n"
            f"• 📊 **थेट विद्यार्थी रेकॉर्ड**: चालू हजेरी टक्केवारी, सीजीपीए (CGPA) आणि उर्वरित फी शिल्लक तपासा\n"
            f"• 🪪 **डिजिटल आयडी पास**: ३D डिजिटल विद्यार्थी ओळखपत्र पहा व फिरवा\n"
            f"• 📄 **बोनाफाइड प्रमाणपत्र**: त्वरित कॉलेज लेटरहेड ड्राफ्ट तयार करा आणि प्रिंट करा\n"
            f"• 🏛️ **कॅम्पस सुविधा**: वायफाय (Wi-Fi), पार्किंग, ग्रंथालय, कॅन्टीन मेनू आणि मेडिकल सेंटर\n"
            f"• 🗺️ **कॅम्पस नकाशा**: सर्व ४ मजल्यांवरील वर्गखोल्या, लॅब आणि सेमिनार हॉल शोधा\n\n"
            f"👉 **त्वरित साधने:**\n"
            f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर</button> "
            f"<button class='action-pill-btn' onclick='openIdCardModal()'>🪪 डिजिटल आयडी पास</button> "
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📄 बोनाफाइड प्रमाणपत्र</button> "
            f"<button class='action-pill-btn' onclick='openMapModal()'>🗺️ फ्लोअर नकाशा</button>\n\n"
            f"*(प्रत्यक्ष मदतीसाठी सेंट्रल ॲडमिन काउंटर ४ ला भेट द्या किंवा +९१ २०-६७५२८००० वर संपर्क साधा)*"
        )
    elif lang == "hi":
        return (
            f"मुझे *\"{message}\"* के लिए सीधा उत्तर नहीं मिला।\n\n"
            f"आधिकारिक **जीएच रायसोनी कॉलेज स्मार्ट सहायक** के रूप में मैं इन विषयों में आपकी सहायता कर सकता हूँ:\n"
            f"• 🎯 **उपस्थिति व बंक सिम्युलेटर**: पूछें *'क्या मैं आज 2 क्लास मिस कर सकता हूँ?'* या *'क्या मैं बंक कर सकता हूँ?'*\n"
            f"• 📊 **छात्र रिकॉर्ड**: अपनी वास्तविक उपस्थिति प्रतिशत, सीजीपीए (CGPA) और बकाया फीस देखें\n"
            f"• 🪪 **डिजिटल आईडी पास**: अपना 3D डिजिटल छात्र पहचान पत्र देखें\n"
            f"• 📄 **बोनाफाइड प्रमाण पत्र**: तुरंत आधिकारिक बोनाफाइड ड्राफ्ट देखें और प्रिंट करें\n"
            f"• 🏛️ **परिसर सुविधाएं**: वाई-फाई (Wi-Fi), पार्किंग, पुस्तकालय, कैंटीन मेन्यू व मेडिकल सेंटर\n"
            f"• 🗺️ **फ्लोर नेविगेटर**: सभी 4 मंजिलों पर कक्षाएं, लैब्स और सेमिनार हॉल खोजें\n\n"
            f"👉 **त्वरित टूल्स:**\n"
            f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर</button> "
            f"<button class='action-pill-btn' onclick='openIdCardModal()'>🪪 डिजिटल आईडी पास</button> "
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📄 बोनाफाइड ड्राफ्ट</button> "
            f"<button class='action-pill-btn' onclick='openMapModal()'>🗺️ फ्लोर नक्शा</button>\n\n"
            f"*(व्यक्तिगत सहायता के लिए सेंट्रल एडमिन काउंटर 4 पर संपर्क करें या +91 20-67528000 पर कॉल करें)*"
        )
    else:
        return (
            f"I couldn't find a direct campus FAQ match for: *\"{message}\"*.\n\n"
            f"As the official **GH Raisoni Campus Smart Assistant**, I can directly help you with:\n"
            f"• 🎯 **Attendance & Bunk Simulator**: Ask *'What if I miss 2 classes today?'* or *'Can I bunk?'*\n"
            f"• 📊 **Live Student Records**: Check real-time attendance percentage, CGPA, and pending fee balance\n"
            f"• 🪪 **Digital ID Pass**: Access your 3D flippable institutional identity card\n"
            f"• 📄 **Bonafide Certificates**: Preview and print official college letterhead drafts\n"
            f"• 🏛️ **Campus Amenities**: Wi-Fi login, parking rules, library hours, canteen menu, and medical center\n"
            f"• 🗺️ **Floor Navigator**: Locate classrooms, seminar halls, and computer labs across all 4 floors\n\n"
            f"👉 **Quick Action Tools:**\n"
            f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Bunk Calculator</button> "
            f"<button class='action-pill-btn' onclick='openIdCardModal()'>🪪 Digital ID Pass</button> "
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📄 Bonafide Draft</button> "
            f"<button class='action-pill-btn' onclick='openMapModal()'>🗺️ Floor Map</button>\n\n"
            f"*(For in-person support, visit Central Admin Counter 4 or call Campus Security at +91 20-67528000)*"
        )


def format_attendance_simulation(student, miss_count, total_conducted, attended, new_total, new_attended, new_pct, diff_pct, lang="en"):
    """Formats attendance what-if impact in English, Marathi, or Hindi."""
    name = student["name"].upper()
    att = float(student["attendance"])

    if new_pct >= 75.0:
        safe_remaining = int(math.floor((new_attended / 0.75) - new_total))
        safe_remaining = max(0, safe_remaining)
        if lang == "mr":
            return (
                f"🎯 **उपस्थिती प्रभाव सिम्युलेटर - {name}**:\n\n"
                f"• चालू उपस्थिती: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                f"• **जर तुम्ही आज {miss_count} व्याख्याने बुडवली तर:**\n"
                f"  - एकूण घेतलेले तास: {total_conducted} ➔ **{new_total}**\n"
                f"  - तुमचे उपस्थित तास: {attended} ➔ **{new_attended}**\n"
                f"  - अंदाजित नवीन हजेरी: **{new_pct}%** ({diff_pct}% ने घसरेल)\n"
                f"• स्थिती: ✅ **सुरक्षित स्थिती** (७५% निकषापेक्षा अधिक)\n"
                f"• सुरक्षित बंक शिल्लक: यानंतरही तुम्ही **{safe_remaining} तास** सुरक्षितपणे बंक करू शकता!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>",
                "Attendance Simulator"
            )
        elif lang == "hi":
            return (
                f"🎯 **उपस्थिति प्रभाव सिम्युलेटर - {name}**:\n\n"
                f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                f"• **यदि आप आज {miss_count} कक्षाएं छोड़ते हैं:**\n"
                f"  - कुल कक्षाएं: {total_conducted} ➔ **{new_total}**\n"
                f"  - आपकी उपस्थिति: {attended} ➔ **{new_attended}**\n"
                f"  - अनुमानित नई उपस्थिति: **{new_pct}%** ({diff_pct}% की कमी)\n"
                f"• स्थिति: ✅ **सुरक्षित स्थिति** (75% कटऑफ से ऊपर)\n"
                f"• सुरक्षित बंक शेष: आप आगे भी **{safe_remaining} कक्षाएं** सुरक्षित रूप से बंक कर सकते हैं!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>",
                "Attendance Simulator"
            )
        else:
            return (
                f"🎯 **ATTENDANCE IMPACT SIMULATOR FOR {name}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Standing: ✅ **SAFE / GOOD STANDING** (Above 75% cutoff)\n"
                f"• Safe Buffer: You can still safely miss up to **{safe_remaining} more lecture(s)** afterwards!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Attendance Simulator"
            )

    elif att >= 75.0 and new_pct < 75.0:
        if lang == "mr":
            return (
                f"🚨 **हजेरी तुटवडा धोका - {name}**:\n\n"
                f"• चालू उपस्थिती: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                f"• **जर तुम्ही आज {miss_count} व्याख्याने बुडवली तर:**\n"
                f"  - एकूण घेतलेले तास: {total_conducted} ➔ **{new_total}**\n"
                f"  - तुमचे उपस्थित तास: {attended} ➔ **{new_attended}**\n"
                f"  - अंदाजित नवीन हजेरी: **{new_pct}%** ({diff_pct}% ने घसरेल)\n"
                f"• स्थिती: ⚠️ **अनिवार्य ७५% निकषाच्या खाली जाईल!**\n"
                f"• इशारा: आज {miss_count} तास गैरहजर राहिल्यास तुम्ही डिटेन्शन धोक्यात याल!\n"
                f"• सल्ला: 🛑 **आज अजिबात गैरहजर राहू नका.** परीक्षेची पात्रता कायम ठेवा!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>",
                "Attendance Alert"
            )
        elif lang == "hi":
            return (
                f"🚨 **उपस्थिति कमी का खतरा - {name}**:\n\n"
                f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                f"• **यदि आप आज {miss_count} कक्षाएं छोड़ते हैं:**\n"
                f"  - कुल कक्षाएं: {total_conducted} ➔ **{new_total}**\n"
                f"  - आपकी उपस्थिति: {attended} ➔ **{new_attended}**\n"
                f"  - अनुमानित नई उपस्थिति: **{new_pct}%** ({diff_pct}% की गिरावट)\n"
                f"• स्थिति: ⚠️ **अनिवार्य 75% सीमा से नीचे आ जाएगी!**\n"
                f"• चेतावनी: आज {miss_count} कक्षाएं छोड़ने पर आप डिटेंशन दायरे में आ जाएंगे!\n"
                f"• सलाह: 🛑 **आज कक्षा मिस न करें।** परीक्षा पात्रता बनाए रखें!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>",
                "Attendance Alert"
            )
        else:
            return (
                f"🚨 **ATTENDANCE SHORTAGE RISK FOR {name}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Standing: ⚠️ **DROPS BELOW 75% MANDATORY CUTOFF!**\n"
                f"• Warning: Missing {miss_count} lecture(s) today pushes you into the detention warning bracket!\n"
                f"• Recommendation: 🛑 **Do NOT miss classes today.** Maintain your exam eligibility!\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Attendance Alert"
            )

    else:
        needed = int(math.ceil(((0.75 * new_total) - new_attended) / 0.25))
        needed = max(1, needed)
        if lang == "mr":
            return (
                f"🚨 **हजेरी डिटेन्शन इशारा - {name}**:\n\n"
                f"• चालू उपस्थिती: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                f"  *(नोंद: तुमची हजेरी आधीच ७५% पेक्षा कमी आहे)*\n"
                f"• **जर तुम्ही आज {miss_count} व्याख्याने बुडवली तर:**\n"
                f"  - एकूण घेतलेले तास: {total_conducted} ➔ **{new_total}**\n"
                f"  - तुमचे उपस्थित तास: {attended} ➔ **{new_attended}**\n"
                f"  - अंदाजित नवीन हजेरी: **{new_pct}%** ({diff_pct}% ने आणखी घसरेल)\n"
                f"• परिणाम: ❌ **डिटेन्शन तुटवडा आणखी गंभीर होईल!**\n"
                f"• रिकव्हरी टार्गेट: ७५% गाठण्यासाठी यानंतर तुम्हाला **सलग {needed} तास १००% उपस्थित राहावे लागेल**.\n"
                f"• प्राध्यापक मार्गदर्शक: **{student['mentor']}** (ॲडमिन ब्लॉक काउंटर ४) यांच्याशी संपर्क साधा.\n"
                f"• त्वरित सूचना: 🛑 आज तास बुडवू नका. आजारी असल्यास ४८ तासांच्या आत डॉक्टरांचे प्रमाणपत्र सादर करा.\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>",
                "Detention Alert"
            )
        elif lang == "hi":
            return (
                f"🚨 **उपस्थिति डिटेंशन चेतावनी - {name}**:\n\n"
                f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                f"  *(नोट: आपकी उपस्थिति पहले ही 75% से नीचे है)*\n"
                f"• **यदि आप आज {miss_count} कक्षाएं छोड़ते हैं:**\n"
                f"  - कुल कक्षाएं: {total_conducted} ➔ **{new_total}**\n"
                f"  - आपकी उपस्थिति: {attended} ➔ **{new_attended}**\n"
                f"  - अनुमानित नई उपस्थिति: **{new_pct}%** ({diff_pct}% की और गिरावट)\n"
                f"• परिणाम: ❌ **डिटेंशन का खतरा और गहरा जाएगा!**\n"
                f"• रिकवरी लक्ष्य: 75% तक पहुंचने के लिए आपको आगे **लगातार {needed} कक्षाएं 100% उपस्थित** रहनी होंगी।\n"
                f"• शिक्षक मार्गदर्शक: **{student['mentor']}** (एडमिन काउंटर 4) से संपर्क करें।\n"
                f"• सुझाव: 🛑 आज कक्षा न छोड़ें। अस्वस्थ होने पर 48 घंटे में मेडिकल सर्टिफिकेट जमा करें।\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>",
                "Detention Alert"
            )
        else:
            return (
                f"🚨 **ATTENDANCE SHORTAGE ALERT FOR {name}**:\n\n"
                f"• Current Attendance: **{att}%** ({attended}/{total_conducted} conducted lectures attended)\n"
                f"  *(Note: You are already in the detention warning bracket below 75%)*\n"
                f"• **If you miss {miss_count} lecture(s) today:**\n"
                f"  - Total Conducted: {total_conducted} ➔ **{new_total}**\n"
                f"  - Your Attended: {attended} ➔ **{new_attended}**\n"
                f"  - Projected Attendance: **{new_pct}%** (drops by {diff_pct}%)\n"
                f"• Impact: ❌ **Deepens your detention shortage!**\n"
                f"• Recovery Target: After missing today, you must attend **{needed} consecutive lectures** with 0 absences to climb back to 75%.\n"
                f"• Faculty Mentor: Contact **{student['mentor']}** at Admin Block Counter 4.\n"
                f"• Urgent Advice: 🛑 We strongly advise attending all lectures today. If medically unwell, submit a registered doctor certificate within 48 hours.\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                "Detention Alert"
            )


def format_bunk_calculator(student, att, attended, total_conducted, bunkable, new_pct, needed, is_safe, lang="en"):
    """Formats bunk calculator response in English, Marathi, or Hindi."""
    name = student["name"]
    if is_safe:
        if bunkable > 0:
            if lang == "mr":
                return (
                    f"🎯 **स्मार्ट बंक कॅल्क्युलेटर - {name}**:\n\n"
                    f"• सध्याची हजेरी: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                    f"• शैक्षणिक स्थिती: ✅ **सुरक्षित स्थिती** (७५% पेक्षा जास्त)\n"
                    f"• सुरक्षित बंक मर्यादा: तुम्ही अजून **{bunkable} व्याख्याने** सुरक्षितपणे बंक करू शकता! 🎉\n"
                    f"• अंदाज: {bunkable} बंक केल्यानंतर तुमची हजेरी अंदाजे **{new_pct}%** राहील.\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>",
                    "Bunk Calculator"
                )
            elif lang == "hi":
                return (
                    f"🎯 **स्मार्ट बंक कैलकुलेटर - {name}**:\n\n"
                    f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                    f"• स्थिति: ✅ **सुरक्षित स्थिति** (75% से ऊपर)\n"
                    f"• सुरक्षित बंक मार्जिन: आप अभी भी **{bunkable} कक्षाएं** सुरक्षित रूप से बंक कर सकते हैं! 🎉\n"
                    f"• पूर्वानुमान: {bunkable} कक्षाएं बंक करने के बाद आपकी उपस्थिति लगभग **{new_pct}%** होगी।\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>",
                    "Bunk Calculator"
                )
            else:
                return (
                    f"🎯 SMART BUNK CALCULATOR for {name}:\n\n"
                    f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                    f"• Academic Standing: ✅ Safe / Good Standing (Above 75%)\n"
                    f"• Safe Bunks Margin: You can safely miss up to **{bunkable} lecture(s)** and still remain above 75%! 🎉\n"
                    f"• Forecast: After bunking {bunkable} classes, your attendance will be approximately {new_pct}%.\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                    "Bunk Calculator"
                )
        else:
            if lang == "mr":
                return (
                    f"🎯 **स्मार्ट बंक कॅल्क्युलेटर - {name}**:\n\n"
                    f"• सध्याची हजेरी: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                    f"• स्थिती: ⚠️ **नेमके ७५% सीमारेषेवर**\n"
                    f"• सुरक्षित बंक मर्यादा: **० तास**. १ तास जरी बुडवला तरी तुम्ही ७५% च्या खाली जाल!\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कॅल्क्युलेटर उघडा</button>",
                    "Bunk Calculator"
                )
            elif lang == "hi":
                return (
                    f"🎯 **स्मार्ट बंक कैलकुलेटर - {name}**:\n\n"
                    f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                    f"• स्थिति: ⚠️ **ठीक 75% सीमा रेखा पर**\n"
                    f"• सुरक्षित बंक मार्जिन: **0 कक्षाएं**। 1 कक्षा भी छोड़ने पर आप 75% से नीचे आ जाएंगे!\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 बंक कैलकुलेटर खोलें</button>",
                    "Bunk Calculator"
                )
            else:
                return (
                    f"🎯 SMART BUNK CALCULATOR for {name}:\n\n"
                    f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                    f"• Status: ⚠️ Right at 75% Boundary\n"
                    f"• Safe Bunk Margin: **0 classes**. Missing even 1 single lecture will push you below 75% and trigger the detention bracket!\n\n"
                    f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Interactive Bunk Tool</button>",
                    "Bunk Calculator"
                )
    else:
        if lang == "mr":
            return (
                f"🚨 **हजेरी रिकव्हरी व बंक तपासणी - {name}**:\n\n"
                f"• चालू हजेरी: **{att}%** ({attended}/{total_conducted} तास उपस्थित)\n"
                f"• तुम्ही बंक करू शकता का? **कदापि नाही! तुम्ही सध्या डिटेन्शन कक्षेत आहात.**\n"
                f"• रिकव्हरी टार्गेट: सुरक्षित ७५% पातळी गाठण्यासाठी तुम्हाला **सलग {needed} तास १००% उपस्थित राहावे लागेल**.\n"
                f"• अंदाज: {needed} तासांना हजर राहिल्यास तुमची हजेरी **{new_pct}%** पर्यंत पोहोचेल.\n"
                f"• मार्गदर्शक: विभागप्रमुख किंवा मेंटॉर **{student['mentor']}** यांच्याशी चर्चा करा.\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 हजेरी रिकव्हरी कॅल्क्युलेटर उघडा</button>",
                "Attendance Recovery"
            )
        elif lang == "hi":
            return (
                f"🚨 **उपस्थिति रिकवरी व बंक अलर्ट - {name}**:\n\n"
                f"• वर्तमान उपस्थिति: **{att}%** ({attended}/{total_conducted} कक्षाएं उपस्थित)\n"
                f"• क्या आप बंक कर सकते हैं? **बिल्कुल नहीं! आप वर्तमान में डिटेंशन दायरे में हैं।**\n"
                f"• रिकवरी लक्ष्य: 75% तक पहुंचने के लिए आपको **लगातार {needed} कक्षाएं 100% उपस्थित** रहनी होंगी।\n"
                f"• पूर्वानुमान: {needed} कक्षाओं में उपस्थित होने पर आपकी उपस्थिति **{new_pct}%** हो जाएगी।\n"
                f"• संपर्क: विभागाध्यक्ष या मेंटॉर **{student['mentor']}** से मिलें।\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 उपस्थिति रिकवरी कैलकुलेटर खोलें</button>",
                "Attendance Recovery"
            )
        else:
            return (
                f"🚨 ATTENDANCE RECOVERY & BUNK ALERT for {name}:\n\n"
                f"• Current Attendance: {att}% ({attended}/{total_conducted} conducted lectures attended)\n"
                f"• Can you bunk? **Strictly NO. You are currently in a detention shortage bracket.**\n"
                f"• Recovery Target: You must attend **{needed} consecutive lectures** without missing any to reach the safe 75% threshold.\n"
                f"• Forecast: Attending {needed} more classes will bring your attendance to {new_pct}%.\n"
                f"• Detention Action: Review the required assignments or prelims with HOD ({student['mentor']}).\n\n"
                f"<button class='action-pill-btn' onclick='openBunkModal()'>🎯 Open Attendance Recovery Calculator</button>",
                "Attendance Recovery"
            )


def format_student_attendance(student, att, attended, total_conducted, lang="en"):
    """Formats official college attendance policy response in user's language."""
    name = student["name"]
    if att >= 75.0:
        if lang == "mr":
            status = "✅ सुरक्षित स्थिती — सेमिस्टर परीक्षेसाठी पूर्ण पात्र"
            advice = "तुमची हजेरी नियमात आहे. ७५% च्या वर टिकवून ठेवा!"
        elif lang == "hi":
            status = "✅ सुरक्षित स्थिति — सेमेस्टर परीक्षा हेतु पूर्णतः पात्र"
            advice = "आपकी उपस्थिति अच्छी है। इसे 75% से ऊपर बनाए रखें!"
        else:
            status = "✅ Good Standing — Fully eligible for semester examinations"
            advice = "Your attendance is in good standing. Keep maintaining it above 75%!"
    elif 60.0 <= att < 75.0:
        if lang == "mr":
            status = "⚠️ डिटेन्शन इशारा (६०% ते ७४.९% वर्ग)"
            advice = (
                "डिटेन्शन धोरणानुसार तुम्हाला पुढील गोष्टी पूर्ण करणे बंधनकारक आहे:\n"
                "• थिअरी: मागील २ वर्षांच्या अंतिम परीक्षा प्रश्नपत्रिका कॉलेजमध्ये ओपन बुक पद्धतीने सोडवाव्या लागतील.\n"
                "• प्रॅक्टिकल: अंतर्गत हजेरी गुण दिले जाणार नाहीत."
            )
        elif lang == "hi":
            status = "⚠️ डिटेंशन चेतावनी (60% से 74.9% वर्ग)"
            advice = (
                "कॉलेज डिटेंशन नीति के अनुसार आपको निम्न कार्य पूरा करना होगा:\n"
                "• थ्योरी: पिछले 2 वर्षों के सेमेस्टर परीक्षा पेपर ओपन बुक मोड में हल करने होंगे।\n"
                "• प्रैक्टिकल: आंतरिक उपस्थिति अंक प्राप्त नहीं होंगे।"
            )
        else:
            status = "⚠️ Detention Warning (60% to 75% Bracket)"
            advice = (
                "Under the college detention policy rubrics, you must complete the following to clear detention:\n"
                "• Theory: End Sem Examination Paper Sets of previous 2 years must be solved in Open Book mode in the College.\n"
                "• Practical: You will not be eligible for the attendance mark component of internal marks."
            )
    elif 50.0 <= att < 60.0:
        if lang == "mr":
            status = "🚨 गंभीर डिटेन्शन तुटवडा (५०% ते ५९.९% वर्ग)"
            advice = (
                "तुम्ही डिटेन आहात जोपर्यंत पुढील गोष्टी पूर्ण होत नाहीत:\n"
                "• थिअरी: (१) मागील २ वर्षांच्या प्रश्नपत्रिका ओपन बुक पद्धतीने सोडवणे, आणि (२) प्रिलिम परीक्षेत बसून किमान ६०% गुण मिळवणे.\n"
                "• प्रॅक्टिकल: प्रॅक्टिकल प्रिलिम परीक्षा देऊन किमान ६०% गुण मिळवणे (एका दिवशी जास्तीत जास्त २ प्रॅक्टिकल)."
            )
        elif lang == "hi":
            status = "🚨 गंभीर डिटेंशन कमी (50% से 59.9% वर्ग)"
            advice = (
                "डिटेंशन नीति के अनुसार आप डिटेन हैं जब तक कि निम्न कार्य पूरा न करें:\n"
                "• थ्योरी: (1) पिछले 2 वर्षों के पेपर ओपन बुक मोड में हल करें, और (2) प्रीलिम परीक्षा में न्यूनतम 60% अंक प्राप्त करें।\n"
                "• प्रैक्टिकल: प्रैक्टिकल प्रीलिम परीक्षा में न्यूनतम 60% अंक प्राप्त करें।"
            )
        else:
            status = "🚨 Critical Detention Shortage (50% to 59.99% Bracket)"
            advice = (
                "Under official detention policy rubrics, you are detained unless you complete:\n"
                "• Theory: (1) End Sem Examination Paper Sets of previous 2 years must be solved in Open Book mode in the College, AND (2) Appear for a prelim examination and score a minimum of 60% marks to be eligible to get out of detention.\n"
                "• Practical: Appear for a practical-based prelim examination and score a minimum of 60% marks (Max 2 practicals conducted in a day)."
            )
    else:
        if lang == "mr":
            status = "❌ थेट डिटेन (५०% पेक्षा कमी हजेरी)"
            advice = "कॉलेज नियमांनुसार ५०% पेक्षा कमी हजेरी असलेल्या विद्यार्थ्यांना सेमिस्टर परीक्षेत बसू दिले जाणार नाही. तात्काळ विभागप्रमुखांना भेटा."
        elif lang == "hi":
            status = "❌ पूर्णतः डिटेन (50% से कम उपस्थिति)"
            advice = "कॉलेज नीति अनुसार 50% से कम उपस्थिति पर कोई विचार नहीं किया जाएगा और छात्र परीक्षा से बाहर रहेगा। तुरंत विभागाध्यक्ष से मिलें।"
        else:
            status = "❌ Strictly Detained (<50% Attendance)"
            advice = "As per college detention policy, students with attendance below 50% have No Consideration and are strictly detained from university semester examinations. Contact your HOD immediately."

    btn_text = "🎯 बंक कॅल्क्युलेटर उघडा" if lang == "mr" else ("🎯 बंक कैलकुलेटर खोलें" if lang == "hi" else "🎯 Open Interactive Bunk Calculator")
    greeting = f"नमस्कार {name}," if lang in ["mr", "hi"] else f"Hi {name},"
    label = "तुमची चालू हजेरी" if lang == "mr" else ("आपकी वर्तमान उपस्थिति" if lang == "hi" else "your current attendance is")
    rubrics = "📋 कॉलेज नियम व कृती:" if lang == "mr" else ("📋 कॉलेज नियम व आवश्यक कार्रवाई:" if lang == "hi" else "📋 College Rubrics & Action Required:")

    return (
        f"{greeting} {label} **{att}%** ({attended}/{total_conducted} तास/कक्षाएं) — {status}.\n\n"
        f"{rubrics}\n{advice}\n\n"
        f"<button class='action-pill-btn' onclick='openBunkModal()'>{btn_text}</button>",
        "Student Attendance"
    )


def format_student_fees(student, lang="en"):
    """Formats student fee status in user's language."""
    name = student["name"]
    due = student["fees_due"]
    if due and due > 0:
        if lang == "mr":
            return (
                f"नमस्कार {name}, तुमची **₹{due:.0f}** फी शिल्लक आहे. "
                f"तुम्ही ही फी विद्यार्थी ईआरपी पोर्टलवरून किंवा अकाउंट्स काउंटर ४ वर भरू शकता.",
                "Fee Status"
            )
        elif lang == "hi":
            return (
                f"नमस्ते {name}, आपकी **₹{due:.0f}** फीस बकाया है। "
                f"आप छात्र ईआरपी पोर्टल या अकाउंट्स काउंटर 4 पर इसका भुगतान कर सकते हैं।",
                "Fee Status"
            )
        else:
            return (
                f"Hi {name}, you have Rs {due:.0f} in pending fees. "
                f"You can pay online via the student ERP portal or at Accounts Counter 4.",
                "Fee Status"
            )
    else:
        if lang == "mr":
            return f"नमस्कार {name}, तुमची कोणतीही फी शिल्लक नाही. सर्व फी पूर्ण भरलेली आहे! 🎉", "Fee Status"
        elif lang == "hi":
            return f"नमस्ते {name}, आपकी कोई फीस बकाया नहीं है। सभी देय राशि पूर्णतः चुकता है! 🎉", "Fee Status"
        else:
            return f"Hi {name}, you have no pending fees. You're completely all clear! 🎉", "Fee Status"


def format_student_cgpa(student, lang="en"):
    """Formats student CGPA status in user's language."""
    name = student["name"]
    cgpa = student["cgpa"]
    course = student["course"]
    sem = student["semester"]
    if lang == "mr":
        return (
            f"नमस्कार {name}, तुमचा सध्याचा CGPA **{cgpa} / १०.०** आहे "
            f"({course}, {sem}). अभिनंदन! अशीच प्रगती सुरू ठेवा! 🌟",
            "Student CGPA"
        )
    elif lang == "hi":
        return (
            f"नमस्ते {name}, आपका वर्तमान CGPA **{cgpa} / 10.0** है "
            f"({course}, {sem})। बधाई! शानदार प्रदर्शन जारी रखें! 🌟",
            "Student CGPA"
        )
    else:
        return (
            f"Hi {name}, your current CGPA is {cgpa} / 10.0 in {course} ({sem}). Keep up the great work! 🌟",
            "Student CGPA"
        )


def format_bonafide(student, lang="en"):
    """Formats bonafide certificate action card in user's language."""
    name = student["name"]
    roll = student["roll_no"]
    course = student["course"]
    sem = student["semester"]
    if lang == "mr":
        return (
            f"📄 **अधिकृत डिजिटल बोनाफाइड प्रमाणपत्र सेवा**\n\n"
            f"प्रमाणित विद्यार्थी: **{name}** ({roll})\n"
            f"अभ्यासक्रम: {course}, {sem}\n\n"
            f"तुमचा बोनाफाइड प्रमाणपत्र ड्राफ्ट तयार आहे. खालील बटणावर क्लिक करून डिजिटल प्रत पहा व प्रिंट करा:\n\n"
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📜 बोनाफाइड प्रमाणपत्र उघडा</button>",
            "Bonafide Service"
        )
    elif lang == "hi":
        return (
            f"📄 **आधिकारिक डिजिटल बोनाफाइड प्रमाण पत्र सेवा**\n\n"
            f"सत्यापित छात्र: **{name}** ({roll})\n"
            f"पाठ्यक्रम: {course}, {sem}\n\n"
            f"आपका बोनाफाइड ड्राफ्ट तैयार है। नीचे दिए गए बटन पर क्लिक कर डिजिटल प्रति देखें और प्रिंट करें:\n\n"
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📜 बोनाफाइड प्रमाण पत्र खोलें</button>",
            "Bonafide Service"
        )
    else:
        return (
            f"📄 OFFICIAL DIGITAL BONAFIDE & DOCUMENT PORTAL:\n\n"
            f"Verified Student Record: {name} ({roll})\n"
            f"Program: {course}, {sem}\n\n"
            f"Your institutional Bonafide Certificate draft is ready for instant viewing and printing!\n\n"
            f"👉 Tap the button below to preview your official college letterhead draft:\n"
            f"<button class='action-pill-btn' onclick='openBonafideModal()'>📜 View & Print Official Bonafide</button>",
            "Bonafide Service"
        )


def format_id_card(student, lang="en"):
    """Formats 3D ID Card modal trigger card in user's language."""
    name = student["name"]
    roll = student["roll_no"]
    if lang == "mr":
        return (
            f"🪪 **३D डिजिटल विद्यार्थी ओळखपत्र (ID Pass)**\n\n"
            f"विद्यार्थी: **{name}** ({roll})\n"
            f"वैशिष्ट्ये: ३D फ्लिप, क्युआर कोड आणि बारकोड पडताळणी.\n\n"
            f"<button class='action-pill-btn' onclick='openIdCardModal()'>✨ ३D डिजिटल आयडी उघडा</button>",
            "Digital ID Pass"
        )
    elif lang == "hi":
        return (
            f"🪪 **3D डिजिटल छात्र पहचान पत्र (ID Pass)**\n\n"
            f"छात्र: **{name}** ({roll})\n"
            f"विशेषताएं: 3D फ्लिप, क्यूआर कोड और बारकोड सत्यापन।\n\n"
            f"<button class='action-pill-btn' onclick='openIdCardModal()'>✨ 3D डिजिटल आईडी खोलें</button>",
            "Digital ID Pass"
        )
    else:
        return (
            f"🪪 DIGITAL STUDENT IDENTITY CARD:\n\n"
            f"Digital campus identity credentials for {name} ({roll}) are ready.\n"
            f"Features: 3D Flip, Live Verification QR Code, and Barcode.\n\n"
            f"👉 <button class='action-pill-btn' onclick='openIdCardModal()'>✨ Open 3D Digital Student ID Card</button>",
            "Digital ID Pass"
        )


def format_profile_summary(student, lang="en"):
    """Formats full student profile summary in user's language."""
    name = student["name"]
    roll = student["roll_no"]
    course = student["course"]
    sem = student["semester"]
    cgpa = student["cgpa"]
    att = student["attendance"]
    mentor = student["mentor"]
    exam_date = student["exam_date"]
    due = student["fees_due"]

    fee_str = f"Rs {due:.0f} pending" if due and due > 0 else "All cleared (No dues)"
    if lang == "mr":
        fee_str = f"₹{due:.0f} बाकी" if due and due > 0 else "सर्व फी भरलेली (No dues)"
        return (
            f"👤 **विद्यार्थी प्रोफाईल माहिती**:\n\n"
            f"• पूर्ण नाव: **{name}**\n"
            f"• नोंदणी क्रमांक (PRN): `{roll}`\n"
            f"• अभ्यासक्रम: {course} ({sem})\n"
            f"• सीजीपीए (CGPA): **{cgpa} / १०.०**\n"
            f"• व्याख्यान हजेरी: **{att}%**\n"
            f"• फी शिल्लक: {fee_str}\n"
            f"• मार्गदर्शक प्राध्यापक: {mentor}\n"
            f"• पुढील परीक्षा तारीख: {exam_date}\n\n"
            f"💡 टीप: ३D डिजिटल पास पाहण्यासाठी 'माझे आयडी कार्ड' टॅप करा किंवा सुरक्षित हजेरीसाठी 'मी बंक करू शकतो का?' विचारा.",
            "Student Profile"
        )
    elif lang == "hi":
        fee_str = f"₹{due:.0f} बकाया" if due and due > 0 else "पूर्णतः चुकता (No dues)"
        return (
            f"👤 **छात्र प्रोफ़ाइल सारांश**:\n\n"
            f"• पूरा नाम: **{name}**\n"
            f"• पंजीकरण संख्या (PRN): `{roll}`\n"
            f"• पाठ्यक्रम: {course} ({sem})\n"
            f"• सीजीपीए (CGPA): **{cgpa} / 10.0**\n"
            f"• उपस्थिति: **{att}%**\n"
            f"• फीस बकाया: {fee_str}\n"
            f"• मेंटॉर शिक्षक: {mentor}\n"
            f"• अगली परीक्षा तिथि: {exam_date}\n\n"
            f"💡 टिप: 3D डिजिटल पास देखने के लिए 'मेरा आईडी कार्ड' टैप करें या बंक मार्जिन जानने के लिए 'क्या मैं बंक कर सकता हूँ?' पूछें।",
            "Student Profile"
        )
    else:
        return (
            f"👤 STUDENT PROFILE SUMMARY:\n\n"
            f"• Full Name: {name}\n"
            f"• Registration No: {roll}\n"
            f"• Program: {course} ({sem})\n"
            f"• Cumulative GPA (CGPA): {cgpa} / 10.0\n"
            f"• Lecture Attendance: {att}%\n"
            f"• Fee Balance: {fee_str}\n"
            f"• Faculty Mentor: {mentor}\n"
            f"• Next Exam Date: {exam_date}\n\n"
            f"💡 Tip: Tap 'My ID Card' to view your 3D digital pass or ask 'Can I bunk?' for your safe attendance margin.",
            "Student Profile"
        )
