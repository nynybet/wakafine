/* QR Code JavaScript - Clean and Simple */
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Simple QR Code generation starting...');
    
    // Prepare QR data
    const qrData = `PNR: {{ booking.pnr_code|escapejs }}
Route: {{ booking.route.origin|escapejs }} to {{ booking.route.destination|escapejs }}
Date: {{ booking.travel_date|date:"M d, Y"|escapejs }}
Time: {{ booking.travel_date|date:"H:i"|escapejs }}
Bus: {{ booking.bus.bus_name|escapejs }}
Seat: {{ booking.seat.seat_number|escapejs }}
Passenger: {{ booking.customer.get_full_name|default:booking.customer.username|escapejs }}
Amount: Le {{ booking.amount_paid|floatformat:0|escapejs }}
Payment: {{ booking.get_payment_method_display|escapejs }}
Status: {{ booking.get_status_display|escapejs }}`;

    console.log('📄 QR Data:', qrData);

    const qrContainer = document.getElementById('qr-code');
    if (!qrContainer) {
        console.error('❌ QR container not found');
        return;
    }

    // Fallback function
    function showFallback() {
        console.log('⚠️ Showing fallback QR display');
        qrContainer.innerHTML = `
            <div style="width: 120px; height: 120px; border: 2px dashed #6b7280; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: #f9fafb; margin: 0 auto;">
                <div style="text-align: center; color: #374151;">
                    <div style="font-size: 12px; font-weight: bold; margin-bottom: 4px;">📱 QR CODE</div>
                    <div style="font-size: 10px; font-family: monospace; font-weight: bold;">{{ booking.pnr_code|escapejs }}</div>
                    <div style="font-size: 8px; margin-top: 4px; opacity: 0.7;">SCAN TO VERIFY</div>
                </div>
            </div>`;
    }

    // Simple QR generation
    function generateQR() {
        console.log('🔄 Attempting QR generation...');
        
        if (typeof QRCode === 'undefined') {
            console.error('❌ QRCode library not loaded');
            showFallback();
            return;
        }

        console.log('✅ QRCode library available');

        try {
            // Clear container first
            qrContainer.innerHTML = '';
            
            // Create QR code using constructor
            const qr = new QRCode(qrContainer, {
                text: qrData,
                width: 120,
                height: 120,
                colorDark: '#1f2937',
                colorLight: '#ffffff',
                correctLevel: QRCode.CorrectLevel.M
            });
            
            console.log('✅ QR Code created successfully!');
            
        } catch (error) {
            console.error('❌ QR generation error:', error);
            showFallback();
        }
    }

    // Wait for library, then generate
    let attempts = 0;
    function waitAndGenerate() {
        attempts++;
        
        if (typeof QRCode !== 'undefined') {
            generateQR();
        } else if (attempts < 30) {
            console.log(`⏳ Waiting... (${attempts}/30)`);
            setTimeout(waitAndGenerate, 100);
        } else {
            console.error('❌ Timeout waiting for QRCode library');
            showFallback();
        }
    }
    
    // Start the process
    waitAndGenerate();
});
