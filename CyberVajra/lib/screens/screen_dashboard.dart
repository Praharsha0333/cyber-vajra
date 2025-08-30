import 'dart:async';
import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

// Import the modular widgets used on this screen
import '../widgets/glassmorphic_card.dart';
import '../widgets/info_card.dart';
import '../widgets/statistics_chart.dart';
import '../widgets/recent_activity_card.dart';

// Import the screens we navigate to from the dashboard
import './team_screen.dart' hide GlassmorphicCard;
import './url_scan_screen.dart' hide GlassmorphicCard;
import './apk_scan_screen.dart' hide GlassmorphicCard;

/// The main dashboard screen of the CyberGuard app.
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  // --- STATE MANAGEMENT (No Changes) ---
  String networkStatus = "Checking...";
  int suspiciousCount = 0;
  int safeCount = 0;
  List<String> recentActivity = [];
  late StreamSubscription<List<ConnectivityResult>> connectivitySubscription;
  Timer? _tipTimer;
  int _currentTipIndex = 0;
  final List<String> _cyberTips = [
    "Use a password manager to create and store strong, unique passwords.",
    "Enable two-factor authentication (2FA) on all your important accounts.",
    "Be cautious of phishing emails. Don't click on suspicious links.",
    "Keep your software and applications updated to the latest versions.",
    "Regularly back up your important data to an external drive or cloud service.",
    "Avoid using public Wi-Fi for sensitive transactions.",
  ];

  @override
  void initState() {
    super.initState();
    _checkNetworkStatus();
    _tipTimer = Timer.periodic(const Duration(seconds: 8), (timer) {
      _changeTip();
    });
  }

  @override
  void dispose() {
    connectivitySubscription.cancel();
    _tipTimer?.cancel();
    super.dispose();
  }

  void _changeTip() {
    setState(() {
      _currentTipIndex = (_currentTipIndex + 1) % _cyberTips.length;
    });
  }

  void _checkNetworkStatus() {
    connectivitySubscription =
        Connectivity().onConnectivityChanged.listen((results) {
          setState(() {
            if (results.contains(ConnectivityResult.mobile)) {
              networkStatus = "Mobile Data";
            } else if (results.contains(ConnectivityResult.wifi)) {
              networkStatus = "WiFi";
            } else {
              networkStatus = "Offline";
            }
          });
        });
  }

  void _updateStats(bool suspicious, String log) {
    setState(() {
      if (suspicious) {
        suspiciousCount++;
      } else {
        safeCount++;
      }
      recentActivity.insert(0, log);
    });
  }
  // --- END OF STATE MANAGEMENT ---

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            Image.asset('assets/logobg.png', height: 28, width: 28),
            const SizedBox(width: 12),
            Text(
              "Dashboard",
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: Colors.white,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.group_outlined),
            tooltip: "Our Team",
            onPressed: () => Navigator.push(
                context,
                MaterialPageRoute(
                    builder: (_) => const TeamScreen())),
          ),
        ],
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4.0),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.lightbulb_outline,
                      color: Colors.yellow[600], size: 20),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _cyberTips[_currentTipIndex],
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(color: Colors.grey[400]),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // --- UPDATE: Redesigned Primary Actions ---
            Row(
              children: [
                _buildActionCard(
                  context: context,
                  icon: Icons.link,
                  title: "Scan URL",
                  subtitle: "Check websites for phishing & malware.",
                  onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) =>
                              UrlScanScreen(onScanComplete: _updateStats))),
                ),
                const SizedBox(width: 16),
                _buildActionCard(
                  context: context,
                  icon: Icons.android,
                  title: "Scan APK",
                  subtitle: "Analyze Android apps for threats.",
                  onPressed: () => Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (_) =>
                              ApkScanScreen(onScanComplete: _updateStats))),
                ),
              ],
            ),
            const SizedBox(height: 24),

            // --- KEY STATS ---
            InfoCard(
              icon: Icons.wifi_tethering_rounded,
              title: "Connection Status",
              value: networkStatus,
              color: theme.primaryColor,
            ),
            const SizedBox(height: 24),
            StatisticsChart(
              safeCount: safeCount,
              suspiciousCount: suspiciousCount,
            ),
            const SizedBox(height: 24),

            // --- ACTIVITY LOG ---
            RecentActivityCard(recentActivity: recentActivity),
          ],
        ),
      ),
    );
  }

  /// --- NEW: A helper widget to build the new, larger action cards ---
  Widget _buildActionCard({
    required BuildContext context,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onPressed,
  }) {
    final theme = Theme.of(context);
    return Expanded(
      child: GestureDetector(
        onTap: onPressed,
        child: GlassmorphicCard(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 20.0, horizontal: 8.0),
            child: Column(
              children: [
                Icon(icon, size: 40, color: theme.primaryColor),
                const SizedBox(height: 12),
                Text(
                  title,
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  textAlign: TextAlign.center,
                  style: theme.textTheme.bodySmall
                      ?.copyWith(color: Colors.grey[400]),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

