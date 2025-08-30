import 'package:flutter/material.dart';
import 'package:fraud_detector_app/other/API%20Keys.dart';

// Import the modular widgets and services used on this screen
import '../widgets/glassmorphic_card.dart';
import '../widgets/threat_map.dart';
import '../widgets/malware_treemap_widget.dart';
import '../widgets/CyberCrimeLineChart.dart';
import '../services/AbuseIPDB_api.dart';

/// The "Threat Center" screen of the CyberGuard app.
/// This screen is a data visualization hub for the global threat landscape.
class GlobalDataScreen extends StatelessWidget {
  const GlobalDataScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final threatApi = ThreatDataApi(ApiKeys.abuseIpDb);

    // --- UPDATE: The screen is now wrapped in a Scaffold to hold the AppBar ---
    return Scaffold(
      // --- UPDATE: Added the AppBar to match the other screens ---
      appBar: AppBar(
        title: const Text(
          "🌍 Threat Center",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // --- UPDATE: The old Padding header has been removed ---

            // --- LIVE THREAT MAP (2D HEATMAP) ---
            GlassmorphicCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Live Threat Map",
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "Top attack origins in world",
                      style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey[400]),
                    ),
                    Divider(color: Colors.grey[700], height: 24),
                    SizedBox(
                      height: 300,
                      child: ThreatMap(api: threatApi),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // --- MALWARE DISTRIBUTION CHART ---
            GlassmorphicCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Top Malware Families",
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "total count of detections in last 24 hrs",
                      style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey[400]),
                    ),
                    Divider(color: Colors.grey[700], height: 24),
                    const SizedBox(
                      height: 300,
                      child: TopMalwareDonutChart(),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            // --- ATTACK TRENDS LINE CHART ---
            GlassmorphicCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Attack Trends Over Time",
                      style: theme.textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      "cases of cybercrime per year as per NCRB",
                      style: theme.textTheme.bodySmall?.copyWith(color: Colors.grey[400]),
                    ),
                    Divider(color: Colors.grey[700], height: 24),
                    const SizedBox(
                        height: 250,
                        child: CyberCrimeLineChart()
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

