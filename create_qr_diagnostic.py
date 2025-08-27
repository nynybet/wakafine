#!/usr/bin/env python3
"""
QR Code Diagnostic Tool
Creates a comprehensive diagnostic page to troubleshoot QR code visibility issues
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wakafine_bus.settings")
django.setup()

from bookings.models import Booking


def create_diagnostic_page():
    """Create a comprehensive QR diagnostic page"""

    # Get sample booking data
    booking = Booking.objects.filter(status="confirmed").first()
    if not booking:
        print("❌ No confirmed bookings found")
        return

    diagnostic_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>QR Code Diagnostic Tool</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        
        .diagnostic-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .test-section {{
            border: 2px solid #ddd;
            margin: 20px 0;
            padding: 20px;
            border-radius: 8px;
        }}
        
        .test-section.success {{
            border-color: #10b981;
            background: #f0fdf4;
        }}
        
        .test-section.error {{
            border-color: #ef4444;
            background: #fef2f2;
        }}
        
        .qr-container {{
            width: 150px;
            height: 150px;
            border: 3px solid #000;
            margin: 20px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border-radius: 8px;
        }}
        
        .log-container {{
            background: #1f2937;
            color: #10b981;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
            margin: 20px 0;
        }}
        
        button {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            margin: 5px;
        }}
        
        button:hover {{
            background: #2563eb;
        }}
        
        .status {{
            font-weight: bold;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
            margin: 5px 0;
        }}
        
        .status.pass {{
            background: #10b981;
            color: white;
        }}
        
        .status.fail {{
            background: #ef4444;
            color: white;
        }}
        
        .booking-info {{
            background: #f8fafc;
            padding: 15px;
            border-radius: 6px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="diagnostic-container">
        <h1>🔍 QR Code Diagnostic Tool</h1>
        <p>This page will help diagnose why QR codes aren't appearing in the print template.</p>
        
        <!-- Booking Information -->
        <div class="booking-info">
            <h3>📋 Test Booking Data</h3>
            <p><strong>PNR:</strong> {booking.pnr_code}</p>
            <p><strong>Route:</strong> {booking.route.origin} → {booking.route.destination}</p>
            <p><strong>Date:</strong> {booking.travel_date.strftime('%B %d, %Y')}</p>
            <p><strong>Passenger:</strong> {booking.customer.get_full_name() or booking.customer.username}</p>
            <p><strong>Bus:</strong> {booking.bus.bus_name}</p>
            <p><strong>Seat:</strong> {booking.seat.seat_number if booking.seat else 'Not assigned'}</p>
        </div>
        
        <!-- Diagnostic Log -->
        <div class="log-container" id="diagnostic-log">
            <div>🚀 QR Code Diagnostic Started...</div>
        </div>
        
        <!-- Library Test -->
        <div class="test-section" id="library-test">
            <h3>📚 QR Library Test</h3>
            <div id="library-status">Testing QR library availability...</div>
        </div>
        
        <!-- Basic QR Generation Test -->
        <div class="test-section" id="basic-test">
            <h3>🔧 Basic QR Generation Test</h3>
            <div id="basic-qr-container" class="qr-container">Loading...</div>
            <div id="basic-status">Testing basic QR generation...</div>
        </div>
        
        <!-- Booking Data QR Test -->
        <div class="test-section" id="booking-test">
            <h3>📱 Booking Data QR Test</h3>
            <div id="booking-qr-container" class="qr-container">Loading...</div>
            <div id="booking-status">Testing with real booking data...</div>
        </div>
        
        <!-- Canvas Styling Test -->
        <div class="test-section" id="style-test">
            <h3>🎨 Canvas Styling Test</h3>
            <div id="styled-qr-container" class="qr-container">Loading...</div>
            <div id="style-status">Testing with print-optimized styling...</div>
        </div>
        
        <!-- Controls -->
        <div style="text-align: center; margin: 30px 0;">
            <button onclick="runAllTests()">🔄 Run All Tests</button>
            <button onclick="clearLog()">🗑️ Clear Log</button>
            <button onclick="window.print()">🖨️ Test Print</button>
            <button onclick="testPrintTemplate()">🎯 Test Print Template</button>
        </div>
        
        <!-- Results Summary -->
        <div id="results-summary" style="margin-top: 30px;">
            <h3>📊 Test Results Summary</h3>
            <div id="summary-content">Run tests to see results...</div>
        </div>
    </div>

    <!-- QR Code Library -->
    <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js"></script>
    <script>
        let logElement = document.getElementById('diagnostic-log');
        let testResults = {{}};
        
        function log(message, type = 'info') {{
            const timestamp = new Date().toLocaleTimeString();
            const color = type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#60a5fa';
            logElement.innerHTML += `<div style="color: ${{color}}">[$${{timestamp}}] $${{message}}</div>`;
            logElement.scrollTop = logElement.scrollHeight;
            console.log(message);
        }}
        
        function clearLog() {{
            logElement.innerHTML = '<div>🚀 QR Code Diagnostic Started...</div>';
        }}
        
        function updateTestSection(sectionId, status, message) {{
            const section = document.getElementById(sectionId);
            const statusDiv = section.querySelector('[id$="-status"]');
            
            section.className = `test-section ${{status}}`;
            statusDiv.innerHTML = `<div class="status ${{status}}">${{status.toUpperCase()}}</div> $${{message}}`;
            
            testResults[sectionId] = {{ status, message }};
        }}
        
        // Test 1: QR Library Availability
        function testLibraryAvailability() {{
            log('🔍 Testing QR library availability...');
            
            if (typeof QRCode === 'undefined') {{
                updateTestSection('library-test', 'error', 'QRCode library not loaded');
                log('❌ QRCode library not available', 'error');
                return false;
            }} else {{
                updateTestSection('library-test', 'success', 'QRCode library loaded successfully');
                log('✅ QRCode library is available', 'success');
                return true;
            }}
        }}
        
        // Test 2: Basic QR Generation
        function testBasicQR() {{
            log('🔧 Testing basic QR generation...');
            
            if (!testLibraryAvailability()) {{
                updateTestSection('basic-test', 'error', 'Cannot test - library not available');
                return false;
            }}
            
            try {{
                const container = document.getElementById('basic-qr-container');
                const testData = 'Hello QR Code Test!';
                
                QRCode.toCanvas(testData, {{
                    width: 130,
                    height: 130,
                    margin: 0,
                    color: {{
                        dark: '#000000',
                        light: '#ffffff'
                    }}
                }}, function (error, canvas) {{
                    if (error) {{
                        updateTestSection('basic-test', 'error', `QR generation failed: ${{error.message}}`);
                        log(`❌ Basic QR generation failed: ${{error.message}}`, 'error');
                    }} else {{
                        container.innerHTML = '';
                        container.appendChild(canvas);
                        updateTestSection('basic-test', 'success', 'Basic QR code generated successfully');
                        log('✅ Basic QR generation successful', 'success');
                    }}
                }});
                
                return true;
            }} catch (e) {{
                updateTestSection('basic-test', 'error', `Exception: ${{e.message}}`);
                log(`❌ Basic QR test exception: ${{e.message}}`, 'error');
                return false;
            }}
        }}
        
        // Test 3: Booking Data QR
        function testBookingQR() {{
            log('📱 Testing booking data QR generation...');
            
            if (!testLibraryAvailability()) {{
                updateTestSection('booking-test', 'error', 'Cannot test - library not available');
                return false;
            }}
            
            try {{
                const container = document.getElementById('booking-qr-container');
                const bookingData = `WAKA-FINE BUS TICKET
PNR: {booking.pnr_code}
Passenger: {booking.customer.get_full_name() or booking.customer.username}
Route: {booking.route.origin} to {booking.route.destination}
Date: {booking.travel_date.strftime('%b %d, %Y')} at {booking.travel_date.strftime('%H:%M')}
Bus: {booking.bus.bus_name}
Seat: {booking.seat.seat_number if booking.seat else 'Not assigned'}
Amount: Le {booking.amount_paid}`;
                
                QRCode.toCanvas(bookingData, {{
                    width: 130,
                    height: 130,
                    margin: 0,
                    color: {{
                        dark: '#000000',
                        light: '#ffffff'
                    }},
                    errorCorrectionLevel: 'H'
                }}, function (error, canvas) {{
                    if (error) {{
                        updateTestSection('booking-test', 'error', `Booking QR failed: ${{error.message}}`);
                        log(`❌ Booking QR generation failed: ${{error.message}}`, 'error');
                    }} else {{
                        container.innerHTML = '';
                        container.appendChild(canvas);
                        updateTestSection('booking-test', 'success', 'Booking QR code generated successfully');
                        log('✅ Booking QR generation successful', 'success');
                    }}
                }});
                
                return true;
            }} catch (e) {{
                updateTestSection('booking-test', 'error', `Exception: ${{e.message}}`);
                log(`❌ Booking QR test exception: ${{e.message}}`, 'error');
                return false;
            }}
        }}
        
        // Test 4: Styled QR (Print Template Style)
        function testStyledQR() {{
            log('🎨 Testing styled QR generation (print template style)...');
            
            if (!testLibraryAvailability()) {{
                updateTestSection('style-test', 'error', 'Cannot test - library not available');
                return false;
            }}
            
            try {{
                const container = document.getElementById('styled-qr-container');
                const bookingData = `WAKA-FINE BUS TICKET
PNR: {booking.pnr_code}
Passenger: {booking.customer.get_full_name() or booking.customer.username}
Route: {booking.route.origin} to {booking.route.destination}
Date: {booking.travel_date.strftime('%b %d, %Y')} at {booking.travel_date.strftime('%H:%M')}
Bus: {booking.bus.bus_name}
Seat: {booking.seat.seat_number if booking.seat else 'Not assigned'}
Amount: Le {booking.amount_paid}`;
                
                QRCode.toCanvas(bookingData, {{
                    width: 130,
                    height: 130,
                    margin: 0,
                    color: {{
                        dark: '#000000',
                        light: '#ffffff'
                    }},
                    errorCorrectionLevel: 'H'
                }}, function (error, canvas) {{
                    if (error) {{
                        updateTestSection('style-test', 'error', `Styled QR failed: ${{error.message}}`);
                        log(`❌ Styled QR generation failed: ${{error.message}}`, 'error');
                    }} else {{
                        // Apply print template styling
                        canvas.style.display = 'block';
                        canvas.style.margin = '0 auto';
                        canvas.style.borderRadius = '4px';
                        canvas.style.border = '3px solid #000';
                        canvas.style.background = 'white';
                        canvas.style.padding = '2px';
                        canvas.style.webkitPrintColorAdjust = 'exact';
                        canvas.style.printColorAdjust = 'exact';
                        canvas.style.colorAdjust = 'exact';
                        canvas.style.width = '110px';
                        canvas.style.height = '110px';
                        canvas.style.visibility = 'visible';
                        canvas.style.opacity = '1';
                        
                        container.innerHTML = '';
                        container.appendChild(canvas);
                        updateTestSection('style-test', 'success', 'Styled QR code generated with print optimizations');
                        log('✅ Styled QR generation successful', 'success');
                    }}
                }});
                
                return true;
            }} catch (e) {{
                updateTestSection('style-test', 'error', `Exception: ${{e.message}}`);
                log(`❌ Styled QR test exception: ${{e.message}}`, 'error');
                return false;
            }}
        }}
        
        function updateSummary() {{
            const summaryContent = document.getElementById('summary-content');
            const total = Object.keys(testResults).length;
            const passed = Object.values(testResults).filter(r => r.status === 'success').length;
            const failed = total - passed;
            
            let summary = `<div style="margin: 10px 0;">`;
            summary += `<div>Total Tests: ${{total}}</div>`;
            summary += `<div style="color: #10b981;">✅ Passed: ${{passed}}</div>`;
            summary += `<div style="color: #ef4444;">❌ Failed: ${{failed}}</div>`;
            summary += `</div>`;
            
            if (failed > 0) {{
                summary += `<div style="margin-top: 15px; padding: 10px; background: #fef2f2; border-radius: 6px;">`;
                summary += `<strong>Issues Found:</strong><ul>`;
                
                Object.entries(testResults).forEach(([test, result]) => {{
                    if (result.status === 'error') {{
                        summary += `<li>${{test.replace('-test', '')}}: ${{result.message}}</li>`;
                    }}
                }});
                
                summary += `</ul></div>`;
            }}
            
            summaryContent.innerHTML = summary;
        }}
        
        function runAllTests() {{
            log('🚀 Starting comprehensive QR diagnostic tests...');
            clearLog();
            
            setTimeout(() => {{ testLibraryAvailability(); }}, 100);
            setTimeout(() => {{ testBasicQR(); }}, 500);
            setTimeout(() => {{ testBookingQR(); }}, 1000);
            setTimeout(() => {{ testStyledQR(); }}, 1500);
            setTimeout(() => {{ updateSummary(); }}, 2000);
        }}
        
        function testPrintTemplate() {{
            log('🎯 Opening actual print template for comparison...');
            const printUrl = '/bookings/{booking.id}/ticket/print/';
            window.open(printUrl, '_blank');
        }}
        
        // Auto-run tests when page loads
        document.addEventListener('DOMContentLoaded', function() {{
            log('📱 QR Diagnostic Tool loaded');
            setTimeout(runAllTests, 500);
        }});
    </script>
</body>
</html>"""

    # Write diagnostic file
    diagnostic_file = "qr_diagnostic.html"
    with open(diagnostic_file, "w", encoding="utf-8") as f:
        f.write(diagnostic_html)

    print(f"✅ QR Diagnostic page created: {diagnostic_file}")
    print(f"🔗 Open in browser: file://{os.path.abspath(diagnostic_file)}")
    print(f"📋 Testing with booking: {booking.pnr_code}")

    return diagnostic_file


if __name__ == "__main__":
    create_diagnostic_page()
