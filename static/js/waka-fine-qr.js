/**
 * Unified QR Code Generation for Waka-Fine Bus Tickets
 * This script provides consistent QR code generation across all ticket pages
 * with proper round trip support and fallback handling.
 */

function generateWakaFineQRCode(bookingData, qrContainer, options = {}) {
    'use strict';
    
    const defaults = {
        width: 130,
        height: 130,
        margin: 0,
        errorCorrectionLevel: 'H',
        showLogs: true,
        useCurrentUrl: true,
        ticketUrl: null
    };
    
    const config = { ...defaults, ...options };
    
    if (config.showLogs) {
        console.log('🚀 Waka-Fine QR Code Generation Starting...');
        console.log('📋 Booking Data:', bookingData);
    }
    
    // Create comprehensive QR ticket data
    let qrTicketData = {
        pnr: bookingData.pnr,
        passenger: bookingData.passenger,
        route: `${bookingData.origin} → ${bookingData.destination}`,
        outbound: {
            date: bookingData.date,
            time: bookingData.time,
            bus: bookingData.bus,
            seat: bookingData.seat
        },
        amount: bookingData.amount,
        status: bookingData.status
    };
    
    // Add return trip details ONLY if it's a round trip and has return data
    if (bookingData.is_round_trip && (bookingData.return_date || bookingData.return_bus || bookingData.return_seat)) {
        qrTicketData.trip_type = 'Round Trip';
        qrTicketData.return = {};
        
        if (bookingData.return_date) {
            qrTicketData.return.date = bookingData.return_date;
        }
        if (bookingData.return_time) {
            qrTicketData.return.time = bookingData.return_time;
        }
        if (bookingData.return_bus) {
            qrTicketData.return.bus = bookingData.return_bus;
        }
        if (bookingData.return_seat) {
            qrTicketData.return.seat = bookingData.return_seat;
        }
    } else {
        qrTicketData.trip_type = 'One Way';
    }
    
    // Determine QR data URL
    const qrDataUrl = config.ticketUrl || (config.useCurrentUrl ? window.location.href : '');
    
    if (config.showLogs) {
        console.log('🎫 QR Ticket Data:', qrTicketData);
        console.log('🔗 QR URL:', qrDataUrl);
    }
    
    function showFallback(reason = 'Unknown') {
        if (config.showLogs) {
            console.log(`⚠️ Using fallback QR display. Reason: ${reason}`);
        }
        
        const isRoundTrip = bookingData.is_round_trip && (bookingData.return_date || bookingData.return_bus || bookingData.return_seat);
        
        qrContainer.innerHTML = `
            <div class="qr-fallback" style="width: 110px; height: 110px; border: 3px solid #2563eb; border-radius: 4px; display: flex; align-items: center; justify-content: center; background: white; margin: 0 auto; -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; color-adjust: exact !important;">
                <div style="text-align: center; color: #2563eb;">
                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 4px;">🎫 TICKET</div>
                    <div style="font-size: 12px; font-family: monospace; font-weight: bold;">${bookingData.pnr}</div>
                    <div style="font-size: 10px; margin-top: 2px;">${bookingData.origin} → ${bookingData.destination}</div>
                    ${isRoundTrip ? '<div style="font-size: 9px; margin-top: 2px; color: #1d4ed8;">ROUND TRIP</div>' : ''}
                </div>
            </div>`;
    }
    
    function generateQR() {
        if (typeof QRCode === 'undefined') {
            console.error('❌ QRCode library is not available.');
            showFallback('Library not loaded');
            return;
        }
        
        try {
            QRCode.toCanvas(qrDataUrl, {
                width: config.width,
                height: config.height,
                margin: config.margin,
                color: {
                    dark: '#2563eb',
                    light: '#ffffff'
                },
                errorCorrectionLevel: config.errorCorrectionLevel
            }, function (error, canvas) {
                if (error) {
                    console.error('❌ QR generation failed:', error);
                    showFallback('QR generation error');
                } else {
                    if (config.showLogs) {
                        console.log('✅ QR Code generated successfully!');
                        console.log('📊 Final QR Data:', qrTicketData);
                    }
                    
                    // Style the canvas
                    canvas.style.cssText = `
                        display: block;
                        margin: 0 auto;
                        border-radius: 4px;
                        border: 3px solid #2563eb;
                        background: white;
                        padding: 2px;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                        width: 110px;
                        height: 110px;
                        -webkit-print-color-adjust: exact;
                        print-color-adjust: exact;
                        color-adjust: exact;
                        visibility: visible;
                        opacity: 1;
                    `;
                    
                    // Clear container and add canvas
                    qrContainer.innerHTML = '';
                    qrContainer.appendChild(canvas);
                    
                    // Set global ready flag
                    window.qrCodeReady = true;
                }
            });
        } catch (e) {
            console.error('❌ QR generation exception:', e);
            showFallback('QR generation exception');
        }
    }
    
    // Wait for QRCode library to load
    function waitForLibrary(attempts = 0) {
        if (typeof QRCode !== 'undefined') {
            generateQR();
        } else if (attempts < 30) {
            setTimeout(() => waitForLibrary(attempts + 1), 200);
        } else {
            showFallback('Library timeout');
        }
    }
    
    // Initialize
    window.qrCodeReady = false;
    waitForLibrary();
}

// Export for use in different contexts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = generateWakaFineQRCode;
}
window.generateWakaFineQRCode = generateWakaFineQRCode;
