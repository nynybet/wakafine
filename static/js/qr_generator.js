/**
 * Waka-Fine QR Code Generation Utility
 * 
 * This script handles the generation of QR codes for tickets.
 * It ensures the QR code library is loaded, prepares the data,
 * and renders the QR code, with a robust fallback if anything fails.
 */
function generateTicketQRCode(qrDataString, containerId) {
    const qrContainer = document.getElementById(containerId);

    // 1. Verify the container exists
    if (!qrContainer) {
        console.error(`[QR] Fatal: Container with ID #${containerId} not found.`);
        return;
    }

    // 2. Verify the QRCode library is available
    if (typeof QRCode === 'undefined') {
        console.error('[QR] Fatal: QRCode library is not loaded.');
        showFallback('Library not loaded');
        return;
    }

    // 3. Define the fallback function
    function showFallback(reason = 'Unknown Error') {
        console.warn(`[QR] Fallback triggered. Reason: ${reason}`);
        const pnr = qrDataString.split('\n')[1].split(': ')[1] || 'N/A';
        qrContainer.innerHTML = `
            <div style="width: 120px; height: 120px; border: 2px solid #1f2937; border-radius: 8px; display: flex; align-items: center; justify-content: center; background: white; margin: 0 auto; text-align: center; color: #1f2937; padding: 5px;">
                <div>
                    <div style="font-size: 12px; font-weight: bold; margin-bottom: 4px;">QR CODE</div>
                    <div style="font-size: 11px; font-family: monospace; font-weight: bold; word-break: break-all;">${pnr}</div>
                    <div style="font-size: 9px; margin-top: 4px;">SCAN TO VERIFY</div>
                </div>
            </div>`;
    }

    // 4. Set QR code options
    const options = {
        width: 128,
        height: 128,
        margin: 1,
        color: {
            dark: '#1e3a8a', // A deeper, more professional blue
            light: '#ffffff'
        },
        errorCorrectionLevel: 'H' // High correction level for better scannability
    };

    // 5. Attempt to generate the QR code
    try {
        QRCode.toCanvas(qrDataString, options, function (error, canvas) {
            if (error) {
                console.error('[QR] Generation failed:', error);
                showFallback('Generation error');
            } else {
                // Style the canvas for a professional look
                canvas.style.display = 'block';
                canvas.style.margin = '0 auto';
                canvas.style.borderRadius = '6px';
                canvas.style.background = 'white';
                
                // Clear container and append the canvas
                qrContainer.innerHTML = '';
                qrContainer.appendChild(canvas);
                console.log('[QR] Success: QR Code rendered in container.');
            }
        });
    } catch (e) {
        console.error('[QR] Generation threw an exception:', e);
        showFallback('Execution exception');
    }
}
