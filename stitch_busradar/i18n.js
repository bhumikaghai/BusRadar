/**
 * BusRadar Universal i18n Localization Engine
 * English ⇄ Hindi Real-Time Seamless Toggle with localStorage persistence.
 */

const BUSRADAR_I18N = {
    en: {
        "app_title": "BusRadar",
        "lang_toggle_btn": "🌐 हि / EN",
        "corridor_badge": "Yamuna Nagar ⇄ MMDU Mullana",
        
        // Onboarding
        "onboard_pass_btn": "Continue as Passenger",
        "onboard_pass_sub": "No login required to track buses",
        "onboard_or": "or",
        "onboard_driver_btn": "Authorized Driver Login",
        "onboard_terms": "By continuing, you agree to BusRadar's",
        "onboard_terms_link": "Terms of Service",

        // OTP
        "otp_badge": "OPERATIONAL GATEWAY",
        "otp_title": "Driver Authentication",
        "otp_desc": "Enter your 10-digit mobile number to access the driver telemetry dispatch node.",
        "otp_phone_label": "DRIVER MOBILE NUMBER",
        "otp_send_btn": "Send OTP",
        "otp_sec_title": "Security Verification",
        "otp_enter_code": "Enter 4-digit code sent to your phone",
        "otp_demo_badge": "DEMO PIN: 0000",
        "otp_verify_btn": "Verify & Enter Console",
        "otp_resend_txt": "Didn't receive code?",
        "otp_resend_btn": "Resend OTP",

        // Driver Dashboard
        "driver_phone_prefix": "Driver: +91 ",
        "driver_exit_btn": "Exit",
        "driver_plate_label": "Vehicle Plate Number",
        "driver_from_label": "From (Starting Stop)",
        "driver_to_label": "To (Destination)",
        "driver_dep_label": "Departure",
        "driver_arr_label": "Arrival",
        "driver_gps_live": "GPS Telemetry: LIVE",
        "driver_rate": "10 Hz Multicast",
        "driver_dispatched": "Packets Dispatched:",
        "driver_view_passenger": "View Passenger Radar",
        "driver_btn_start": "START LIVE BROADCAST",
        "driver_btn_stop": "STOP BROADCASTING",
        "driver_report_delay": "Report Transit Delay",
        "driver_on_time": "ON TIME",
        "driver_delay_5": "+5 Mins",
        "driver_delay_10": "+10 Mins",
        "driver_delay_30": "+30 Mins",
        "driver_delay_clear": "Clear Delay",
        "driver_from_ph": "Search Origin: Yamuna Nagar, Ambala...",
        "driver_to_ph": "Search Destination: MMDU, Kurukshetra...",

        // Passenger Dashboard
        "pass_ws_live": "WEBSOCKET: LIVE",
        "pass_route_title": "Route 104 Express",
        "pass_eta_live": "Live ETA: 12 mins",
        "pass_traffic_optimal": "Optimal Traffic",
        "pass_traffic_delayed": "Delayed by",
        "pass_fare_summary": "Dep: 08:30 AM • Arr: 09:15 AM",
        "pass_buy_btn": "Buy Ticket (UPI Pass)",
        "pass_from_ph": "From: Yamuna Nagar Bus Stand...",
        "pass_to_ph": "To: MMDU Campus Gate, Ambala...",
        "pass_incident_title": "TRANSIT DELAY REPORTED",
        
        // UPI Modal
        "upi_title": "Bharat UPI Instant Pass",
        "upi_corridor_label": "Transit Corridor:",
        "upi_veh_label": "Vehicle ID:",
        "upi_pnr_label": "Generated PNR:",
        "upi_fare_label": "Fare Amount:",
        "upi_scan_hint": "Scan with GPay, PhonePe, or Paytm",
        "upi_pay_btn": "Simulate UPI Payment (Instant Pay)",
        "upi_verifying": "Verifying via UPI Switch...",
        "upi_success_title": "Payment Verified!",
        "upi_success_desc": "Digital Pass Issued to MMDU Mullana",
        "upi_open_journey": "Open Digital Pass in Active Journey",

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
        "journey_view_ticket": "View Digital Pass",
        "journey_btn_sos": "Emergency / SOS",
        "journey_emergency_title": "Emergency / SOS",
        "journey_pass_title": "BusRadar Transit Pass",
        "journey_pass_verified": "OFFLINE VERIFIABLE PASS",
        "journey_on_time": "On Time",
        "journey_delay": "Delay",
        "journey_end_btn": "End Journey",
        "journey_sos_title": "Live Journey Safety (SOS)",
        "journey_sos_desc": "Share your verified live bus location and vehicle telemetry with family or authorities.",
        "journey_sos_copy": "Copy Live Tracking Link",
        "journey_sos_wa": "Dispatch via WhatsApp",
        "journey_sos_call": "Emergency Helpline (112)",
        "stop_ynr": "Yamuna Nagar",
        "stop_mmdu": "MMDU Campus Gate"
    },
    hi: {
        "app_title": "बस-रडार (BusRadar)",
        "lang_toggle_btn": "🌐 EN / हि",
        "corridor_badge": "यमुनानगर ⇄ MMDU मुलाना",

        // Onboarding
        "onboard_pass_btn": "यात्री के रूप में आगे बढ़ें",
        "onboard_pass_sub": "बस ट्रैक करने के लिए लॉगिन की आवश्यकता नहीं है",
        "onboard_or": "अथवा",
        "onboard_driver_btn": "अधिकृत ड्राइवर लॉगिन",
        "onboard_terms": "जारी रखकर, आप बस-रडार की",
        "onboard_terms_link": "सेवा शर्तों से सहमत होते हैं",

        // OTP
        "otp_badge": "ऑपरेशनल गेटवे",
        "otp_title": "ड्राइवर प्रमाणीकरण",
        "otp_desc": "ड्राइवर टेलीमेट्री डिस्पैच नोड तक पहुंचने के लिए अपना 10-अंकों का मोबाइल नंबर दर्ज करें।",
        "otp_phone_label": "ड्राइवर मोबाइल नंबर",
        "otp_send_btn": "OTP भेजें",
        "otp_sec_title": "सुरक्षा सत्यापन",
        "otp_enter_code": "अपने फोन पर भेजा गया 4-अंकों का कोड दर्ज करें",
        "otp_demo_badge": "डेमो पिन: 0000",
        "otp_verify_btn": "सत्यापित करें और कंसोल खोलें",
        "otp_resend_txt": "कोड प्राप्त नहीं हुआ?",
        "otp_resend_btn": "OTP पुनः भेजें",

        // Driver Dashboard
        "driver_phone_prefix": "ड्राइवर: +91 ",
        "driver_exit_btn": "बाहर निकलें",
        "driver_plate_label": "वाहन प्लेट नंबर",
        "driver_from_label": "कहाँ से (प्रारंभिक स्टॉप)",
        "driver_to_label": "कहाँ तक (गंतव्य)",
        "driver_dep_label": "प्रस्थान समय",
        "driver_arr_label": "आगमन समय",
        "driver_gps_live": "GPS टेलीमेट्री: लाइव",
        "driver_rate": "10 Hz मल्टीकास्ट",
        "driver_dispatched": "भेजे गए पैकेट:",
        "driver_view_passenger": "यात्री रडार देखें",
        "driver_btn_start": "लाइव प्रसारण शुरू करें",
        "driver_btn_stop": "प्रसारण रोकें",
        "driver_report_delay": "पारगमन देरी की रिपोर्ट करें",
        "driver_on_time": "समय पर",
        "driver_delay_5": "+5 मिनट",
        "driver_delay_10": "+10 मिनट",
        "driver_delay_30": "+30 मिनट",
        "driver_delay_clear": "देरी साफ़ करें",
        "driver_from_ph": "शुरुआती स्टॉप खोजें: यमुनानगर, अंबाला...",
        "driver_to_ph": "गंतव्य खोजें: MMDU, कुरुक्षेत्र...",

        // Passenger Dashboard
        "pass_ws_live": "वेबसॉकेट: लाइव",
        "pass_route_title": "रूट 104 एक्सप्रेस",
        "pass_eta_live": "लाइव आगमन: 12 मिनट",
        "pass_traffic_optimal": "सुगम यातायात (समय पर)",
        "pass_traffic_delayed": "देरी:",
        "pass_fare_summary": "प्रस्थान: 08:30 AM • आगमन: 09:15 AM",
        "pass_buy_btn": "टिकट खरीदें (UPI पास)",
        "pass_from_ph": "कहाँ से: यमुनानगर बस स्टैंड...",
        "pass_to_ph": "कहाँ तक: MMDU कैंपस गेट, अंबाला...",
        "pass_incident_title": "पारगमन देरी की सूचना",

        // UPI Modal
        "upi_title": "भारत UPI त्वरित पास",
        "upi_corridor_label": "पारगमन मार्ग:",
        "upi_veh_label": "वाहन आईडी:",
        "upi_pnr_label": "जनरेट किया गया PNR:",
        "upi_fare_label": "किराया राशि:",
        "upi_scan_hint": "GPay, PhonePe या Paytm से स्कैन करें",
        "upi_pay_btn": "UPI भुगतान सिमुलेशन (त्वरित भुगतान)",
        "upi_verifying": "UPI स्विच द्वारा सत्यापन जारी...",
        "upi_success_title": "भुगतान सत्यापित!",
        "upi_success_desc": "MMDU मुलाना के लिए डिजिटल पास जारी",
        "upi_open_journey": "सक्रिय यात्रा में डिजिटल पास खोलें",

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
        "journey_view_ticket": "डिजिटल पास देखें",
        "journey_btn_sos": "आपातकाल / SOS",
        "journey_emergency_title": "आपातकाल / SOS",
        "journey_pass_title": "बस-रडार ट्रांजिट पास",
        "journey_pass_verified": "ऑफ़लाइन सत्यापित पास",
        "journey_on_time": "समय पर",
        "journey_delay": "देरी",
        "journey_end_btn": "यात्रा समाप्त करें",
        "journey_sos_title": "लाइव यात्रा सुरक्षा (SOS)",
        "journey_sos_desc": "अपने परिवार या अधिकारियों के साथ अपनी सत्यापित लाइव बस लोकेशन और वाहन टेलीमेट्री साझा करें।",
        "journey_sos_copy": "लाइव ट्रैकिंग लिंक कॉपी करें",
        "journey_sos_wa": "व्हाट्सएप द्वारा भेजें",
        "journey_sos_call": "आपातकालीन हेल्पलाइन (112)",
        "stop_ynr": "यमुनानगर",
        "stop_mmdu": "MMDU कैंपस गेट"
    }
};

function getSavedLang() {
    return localStorage.getItem('busradar_lang') || 'en';
}

function applyLanguage(lang) {
    const dict = BUSRADAR_I18N[lang] || BUSRADAR_I18N.en;
    localStorage.setItem('busradar_lang', lang);

    // Update text nodes with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    // Update placeholders with data-i18n-ph
    document.querySelectorAll('[data-i18n-ph]').forEach(el => {
        const key = el.getAttribute('data-i18n-ph');
        if (dict[key]) {
            el.placeholder = dict[key];
        }
    });

    // Update toggle button text if exists
    const toggleBtn = document.getElementById('btn-lang-toggle');
    if (toggleBtn) {
        toggleBtn.innerHTML = `
            <span class="material-symbols-outlined text-[14px]">translate</span>
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
