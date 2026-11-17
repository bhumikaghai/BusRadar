/**
 * BusRadar Universal i18n Localization Engine
 * English ⇄ Hindi Real-Time Seamless Toggle with localStorage & in-memory fallback.
 */

const BUSRADAR_I18N = {
    en: {
        "app_title": "BusRadar",
        "lang_toggle_btn": "🌐 हि / EN",
        "corridor_badge": "Yamuna Nagar ⇄ MMDU Mullana",
        
        // Onboarding
        "onboard_pass_btn": "Continue as Passenger",
        "onboard_pass_sub": "No login required to track live buses",
        "onboard_or": "or",
        "onboard_driver_btn": "Authorized Driver Login",
        "onboard_terms": "By continuing, you agree to BusRadar's",
        "onboard_terms_link": "Terms of Service",

        // Driver Login
        "otp_badge": "SECURITY GATEWAY",
        "otp_title": "Driver Authentication",
        "otp_desc": "Enter your vehicle plate number and 4-digit security PIN to access the driver console.",
        "otp_phone_label": "DRIVER MOBILE NUMBER",
        "otp_bus_label": "ASSIGNED VEHICLE PLATE",
        "otp_enter_code": "Enter 4-Digit Driver Security PIN",
        "otp_verify_btn": "Verify & Enter Console",
        "otp_locked_notice": "Account locked due to 5 failed attempts.",

        // Driver Dashboard
        "driver_phone_prefix": "Driver: +91 ",
        "driver_exit_btn": "Exit",
        "driver_plate_label": "Vehicle Plate Number",
        "driver_from_label": "From (Starting Stop)",
        "driver_to_label": "To (Destination)",
        "driver_dep_label": "Departure",
        "driver_arr_label": "Arrival",
        "driver_gps_live": "Real GPS: BROADCASTING",
        "driver_gps_idle": "GPS Idle (Not Broadcasting)",
        "driver_accuracy_good": "Accuracy: Good (±",
        "driver_accuracy_fair": "Accuracy: Fair (±",
        "driver_accuracy_poor": "Accuracy: Low (±",
        "driver_rate": "Update Rate",
        "driver_dispatched": "Packets Dispatched:",
        "driver_view_passenger": "View Passenger Radar",
        "driver_btn_start": "START LIVE BROADCAST",
        "driver_btn_stop": "END TRIP & STOP",
        "driver_btn_record_route": "📍 Record New Route",
        "driver_btn_stop_record": "💾 Stop & Save Route",
        "driver_report_delay": "Report Transit Delay",
        "driver_on_time": "ON TIME",
        "driver_delay_5": "+5 Mins",
        "driver_delay_10": "+10 Mins",
        "driver_delay_30": "+30 Mins",
        "driver_delay_clear": "Clear Delay",
        "driver_from_ph": "Search Origin: Yamuna Nagar...",
        "driver_to_ph": "Search Destination: MMDU...",

        // Passenger Dashboard
        "pass_ws_live": "LIVE (<10s ago)",
        "pass_weak_signal": "WEAK SIGNAL (10-30s)",
        "pass_last_seen": "LAST SEEN",
        "pass_trip_ended": "TRIP COMPLETED",
        "pass_no_buses": "No buses currently broadcasting on this corridor",
        "pass_waiting_driver": "Live tracking will activate as soon as an authorized driver starts their trip.",
        "pass_route_title": "Corridor Express",
        "pass_eta_live": "Live ETA",
        "pass_traffic_optimal": "Optimal Traffic (On Time)",
        "pass_traffic_delayed": "Delayed by",
        "pass_fare_summary": "Dep: 08:30 AM • Arr: 09:15 AM",
        "pass_buy_btn": "Bus Pass / Ticketing",
        "pass_ticket_soon_title": "Digital Ticketing Coming Soon",
        "pass_ticket_soon_desc": "Unified cashless ticketing and automated pass issuance will launch in the next release.",
        "pass_from_ph": "From: Yamuna Nagar Bus Stand...",
        "pass_to_ph": "To: MMDU Campus Gate, Ambala...",
        "pass_incident_title": "TRANSIT DELAY REPORTED",

        // Active Journey Dashboard
        "journey_title": "Active Journey",
        "journey_status_active": "ON-BOARD GPS ACTIVE",
        "journey_live_badge": "Live Journey Active",
        "journey_eta_title": "Live ETA",
        "journey_speed_label": "Speed",
        "journey_dist_label": "Distance Remaining",
        "journey_next_stop_label": "Next Stop",
        "journey_arriving_label": "Arriving in:",
        "journey_progress_label": "Corridor Progress",
        "journey_btn_qr": "View Digital Pass",
        "journey_btn_sos": "Emergency / SOS",
        "journey_emergency_title": "Live Journey Safety (SOS)",
        "journey_pass_title": "BusRadar Transit Pass",
        "journey_pass_verified": "Offline Verified Transit Pass",
        "journey_on_time": "ON TIME",
        "journey_delay": "DELAY",
        "journey_end_btn": "End Journey",
        "journey_sos_title": "Live Journey Safety (SOS)",
        "journey_sos_desc": "Share your verified live bus location and vehicle tracking link with family or emergency contacts.",
        "journey_sos_copy": "Copy Live Tracking Link",
        "journey_sos_copied": "Link Copied to Clipboard!",
        "journey_sos_share": "Share Link via Device",
        "stop_ynr": "Yamuna Nagar Stand",
        "stop_mmdu": "MMDU Campus Gate"
    },
    hi: {
        "app_title": "बस-रडार",
        "lang_toggle_btn": "🌐 EN / हि",
        "corridor_badge": "यमुनानगर ⇄ एमएमडीयू मुलाना",

        // Onboarding
        "onboard_pass_btn": "यात्री के रूप में जारी रखें",
        "onboard_pass_sub": "लाइव बस देखने के लिए लॉगिन की आवश्यकता नहीं",
        "onboard_or": "अथवा",
        "onboard_driver_btn": "अधिकृत चालक (ड्राइवर) लॉगिन",
        "onboard_terms": "जारी रखकर, आप बस-रडार के नियमों से सहमत होते हैं",
        "onboard_terms_link": "सेवा की शर्तें",

        // Driver Login
        "otp_badge": "सुरक्षा गेटवे",
        "otp_title": "ड्राइवर प्रमाणीकरण",
        "otp_desc": "ड्राइवर कंसोल तक पहुंचने के लिए अपना वाहन नंबर और 4-अंकीय सुरक्षा पिन दर्ज करें।",
        "otp_phone_label": "ड्राइवर मोबाइल नंबर",
        "otp_bus_label": "आवंटित बस नंबर",
        "otp_enter_code": "4-अंकीय ड्राइवर सुरक्षा पिन दर्ज करें",
        "otp_verify_btn": "सत्यापित करें और कंसोल खोलें",
        "otp_locked_notice": "5 बार गलत पिन डालने के कारण खाता अस्थायी रूप से लॉक है।",

        // Driver Dashboard
        "driver_phone_prefix": "ड्राइवर: +91 ",
        "driver_exit_btn": "लॉगआउट",
        "driver_plate_label": "वाहन नंबर प्लेट",
        "driver_from_label": "प्रारंभिक स्टॉप (From)",
        "driver_to_label": "गंतव्य स्टॉप (To)",
        "driver_dep_label": "प्रस्थान समय",
        "driver_arr_label": "पहुंचने का समय",
        "driver_gps_live": "सच्चा GPS: लाइव प्रसारण चालू",
        "driver_gps_idle": "GPS शांत (प्रसारण बंद)",
        "driver_accuracy_good": "सटीकता: उत्कृष्ट (±",
        "driver_accuracy_fair": "सटीकता: सामान्य (±",
        "driver_accuracy_poor": "सटीकता: कम (±",
        "driver_rate": "अपडेट दर",
        "driver_dispatched": "भेजे गए पैकेट:",
        "driver_view_passenger": "यात्री रडार देखें",
        "driver_btn_start": "लाइव GPS प्रसारण शुरू करें",
        "driver_btn_stop": "यात्रा समाप्त करें और रोकें",
        "driver_btn_record_route": "📍 नया रूट रिकॉर्ड करें",
        "driver_btn_stop_record": "💾 रूट सुरक्षित करें",
        "driver_report_delay": "देरी की सूचना दर्ज करें",
        "driver_on_time": "समय पर",
        "driver_delay_5": "+5 मिनट",
        "driver_delay_10": "+10 मिनट",
        "driver_delay_30": "+30 मिनट",
        "driver_delay_clear": "देरी हटाएं (समय पर)",
        "driver_from_ph": "प्रारंभिक स्टॉप खोजें: यमुनानगर...",
        "driver_to_ph": "गंतव्य स्टॉप खोजें: एमएमडीयू...",

        // Passenger Dashboard
        "pass_ws_live": "लाइव (<10 से. पहले)",
        "pass_weak_signal": "कमजोर सिग्नल (10-30 से.)",
        "pass_last_seen": "अंतिम देखा गया",
        "pass_trip_ended": "यात्रा समाप्त",
        "pass_no_buses": "इस रूट पर वर्तमान में कोई बस लाइव नहीं है",
        "pass_waiting_driver": "जैसे ही कोई चालक यात्रा शुरू करेगा, लाइव ट्रैकिंग यहाँ स्वतः दिखाई देगी।",
        "pass_route_title": "कॉरिडोर एक्सप्रेस",
        "pass_eta_live": "पहुंचने का समय (ETA)",
        "pass_traffic_optimal": "सामान्य यातायात (समय पर)",
        "pass_traffic_delayed": "देरी:",
        "pass_fare_summary": "प्रस्थान: 08:30 AM • आगमन: 09:15 AM",
        "pass_buy_btn": "बस पास / टिकट",
        "pass_ticket_soon_title": "डिजिटल टिकट सुविधा शीघ्र उपलब्ध",
        "pass_ticket_soon_desc": "कैशलेस डिजिटल टिकटिंग और पास जारी करने की सुविधा अगले संस्करण में शुरू होगी।",
        "pass_from_ph": "कहाँ से: यमुनानगर बस स्टैंड...",
        "pass_to_ph": "कहाँ तक: एमएमडीयू कैंपस गेट...",
        "pass_incident_title": "बस देरी की सूचना",

        // Active Journey Dashboard
        "journey_title": "सक्रिय यात्रा",
        "journey_status_active": "ऑन-बोर्ड GPS सक्रिय",
        "journey_live_badge": "लाइव यात्रा चालू है",
        "journey_eta_title": "लाइव आगमन का समय",
        "journey_speed_label": "गति",
        "journey_dist_label": "शेष दूरी",
        "journey_next_stop_label": "अगला स्टॉप",
        "journey_arriving_label": "पहुंचने में समय:",
        "journey_progress_label": "यात्रा प्रगति",
        "journey_btn_qr": "डिजिटल पास देखें",
        "journey_btn_sos": "आपातकाल / SOS",
        "journey_emergency_title": "लाइव यात्रा सुरक्षा (SOS)",
        "journey_pass_title": "बस-रडार ट्रांजिट पास",
        "journey_pass_verified": "ऑफ़लाइन सत्यापित पास",
        "journey_on_time": "समय पर",
        "journey_delay": "देरी",
        "journey_end_btn": "यात्रा समाप्त करें",
        "journey_sos_title": "लाइव यात्रा सुरक्षा (SOS)",
        "journey_sos_desc": "अपने परिवार या संपर्कों के साथ अपनी लाइव बस ट्रैकिंग लिंक साझा करें।",
        "journey_sos_copy": "लाइव ट्रैकिंग लिंक कॉपी करें",
        "journey_sos_copied": "लिंक कॉपी हो गया!",
        "journey_sos_share": "डिवाइस द्वारा शेयर करें",
        "stop_ynr": "यमुनानगर स्टैंड",
        "stop_mmdu": "एमएमडीयू कैंपस गेट"
    }
};

// In-Memory Storage Fallback for Incognito & Strict Privacy Modes
if (typeof window.__memoryStorage === 'undefined') {
    window.__memoryStorage = {};
}

function getSavedLang() {
    try {
        if (window.localStorage) {
            return window.localStorage.getItem('busradar_lang') || 'en';
        }
    } catch (e) {
        return window.__memoryStorage['busradar_lang'] || 'en';
    }
    return window.__memoryStorage['busradar_lang'] || 'en';
}

function applyLanguage(lang) {
    const dict = BUSRADAR_I18N[lang] || BUSRADAR_I18N.en;
    try {
        if (window.localStorage) {
            window.localStorage.setItem('busradar_lang', lang);
        }
    } catch (e) {
        window.__memoryStorage['busradar_lang'] = lang;
    }
    window.__memoryStorage['busradar_lang'] = lang;

    // Update text nodes
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (dict[key]) {
            el.placeholder = dict[key];
        }
    });

    // Update toggle button text if present
    const toggleBtn = document.getElementById('btn-lang-toggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = `
            <span class="material-symbols-outlined text-[15px]">translate</span>
            <span>${lang === 'en' ? 'हिन्दी' : 'English'}</span>
        `;
    }
}

function toggleLanguage() {
    const current = getSavedLang();
    const next = current === 'en' ? 'hi' : 'en';
    applyLanguage(next);
}

// Auto-run on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    applyLanguage(getSavedLang());
    const toggleBtn = document.getElementById('btn-lang-toggle');
    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleLanguage);
    }
});
