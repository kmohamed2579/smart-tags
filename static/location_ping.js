function sendLocation(userId) {
    const modal = document.getElementById('locationModal');
    const allowBtn = document.getElementById('allowLocationBtn');
    const denyBtn = document.getElementById('denyLocationBtn');

    // 1. إظهار النافذة المخصصة بتاعتنا أولاً
    modal.style.display = 'flex';

    // 2. لو المكتشف داس "موافق"
    allowBtn.onclick = function() {
        modal.style.display = 'none'; // نخفي الرسالة بتاعتنا
        
        // هنا بقى نطلب الصلاحية الرسمية بتاعة المتصفح
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(position) {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                // نبعت اللوكيشن للبايثون
                fetch('/ping_location', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: userId,
                        latitude: lat,
                        longitude: lng
                    })
                }).then(response => console.log("تم الإرسال!"));
            }, function(error) {
                console.log("تم رفض الصلاحية الرسمية من المتصفح.");
            });
        }
    };

    // 3. لو المكتشف داس "لا، شكراً"
    denyBtn.onclick = function() {
        modal.style.display = 'none'; // نخفي الرسالة وخلاص
    };
}