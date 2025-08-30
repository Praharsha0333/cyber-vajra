import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';
import '../widgets/scanning_animation.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';

// You should move this to its own file, e.g., 'widgets/glassmorphic_card.dart'
class GlassmorphicCard extends StatelessWidget {
  final Widget child;
  const GlassmorphicCard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16.0),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16.0),
            border: Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1.5,
            ),
          ),
          child: child,
        ),
      ),
    );
  }
}

class UrlScanScreen extends StatefulWidget {
  final void Function(bool suspicious, String log)? onScanComplete;
  const UrlScanScreen({super.key, this.onScanComplete});

  @override
  State<UrlScanScreen> createState() => _UrlScanScreenState();
}

class _UrlScanScreenState extends State<UrlScanScreen> {
  final TextEditingController _urlController = TextEditingController();
  Map<String, dynamic>? _scanResult;
  bool _isLoading = false;

  Future<void> _scanUrl() async {
    String url = _urlController.text.trim();
    if (url.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a URL to scan.')),
      );
      return;
    }
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://$url';
    }
    if (Uri.tryParse(url)?.isAbsolute != true) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('The entered URL is not valid.')),
      );
      return;
    }
    FocusScope.of(context).unfocus();
    setState(() {
      _isLoading = true;
      _scanResult = null;
    });
    Map<String, dynamic> result = {};
    try {
      final stopwatch = Stopwatch()..start();
      result = await ApiService.scanUrl(url);
      stopwatch.stop();
      final remainingTime = const Duration(seconds: 5) - stopwatch.elapsed;
      if (remainingTime > Duration.zero) {
        await Future.delayed(remainingTime);
      }
    } catch (e) {
      result = {'error': 'Failed to scan URL. Please check your connection and try again.'};
    } finally {
      setState(() {
        _isLoading = false;
        _scanResult = result;
      });
    }
    if (widget.onScanComplete != null && result['error'] == null) {
      int riskScore = result['risk_score'] ?? 0;
      bool suspicious = riskScore > 50;
      String log = suspicious
          ? "High risk found for $url ($riskScore%)"
          : "Scanned $url, looks safe.";
      widget.onScanComplete!(suspicious, log);
    }
  }

  Future<void> _pasteFromClipboard() async {
    final clipboardData = await Clipboard.getData(Clipboard.kTextPlain);
    if (clipboardData != null && clipboardData.text != null) {
      _urlController.text = clipboardData.text!;
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text("URL Scanner", style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: theme.primaryColor)),
        centerTitle: true,
        iconTheme: IconThemeData(color: theme.primaryColor),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            children: [
              GlassmorphicCard(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Enter URL", style: theme.textTheme.titleMedium),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _urlController,
                        style: const TextStyle(color: Colors.white),
                        decoration: InputDecoration(
                          hintText: "e.g., www.example.com",
                          hintStyle: TextStyle(color: Colors.grey[600]),
                          filled: true,
                          fillColor: Colors.black.withOpacity(0.3),
                          prefixIcon: IconButton(
                            icon: Icon(Icons.paste, color: Colors.grey[400]),
                            onPressed: _pasteFromClipboard,
                          ),
                          suffixIcon: IconButton(
                            icon: Icon(Icons.search, color: theme.primaryColor),
                            onPressed: _isLoading ? null : _scanUrl,
                          ),
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(12),
                            borderSide: BorderSide.none,
                          ),
                          contentPadding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        onSubmitted: (_) => _scanUrl(),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 500),
                transitionBuilder: (child, animation) => FadeTransition(opacity: animation, child: ScaleTransition(scale: animation, child: child)),
                child: _isLoading
                    ? Padding(
                  key: const ValueKey('loading'),
                  padding: const EdgeInsets.symmetric(vertical: 40.0),
                  child: const ScanningAnimation(),
                )
                    : _scanResult != null
                    ? KeyedSubtree(
                  key: const ValueKey('results'),
                  child: _buildResult(theme),
                )
                    : const SizedBox.shrink(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // --- UPDATE: Complete redesign of the results section ---
  Widget _buildResult(ThemeData theme) {
    if (_scanResult!['error'] != null) {
      return GlassmorphicCard(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error_outline, color: Colors.red[400]),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                    _scanResult!['error'],
                    style: TextStyle(color: Colors.red[300])
                ),
              ),
            ],
          ),
        ),
      );
    }

    // --- Parse all the new data safely ---
    int riskScore = _scanResult!['risk_score'] ?? 0;
    String overallStatus = _scanResult!['overall_status'] ?? 'Unknown';
    String userTip = _scanResult!['user_tip'] ?? 'Proceed with caution.';
    var details = _scanResult!['details'] ?? {};
    var domainAnalysis = details['domain_analysis'] ?? {};
    var reputation = details['reputation_analysis'] ?? {};
    var network = details['network_analysis'] ?? {};
    var visual = details['visual_analysis'] ?? {};
    var mlInsights = _scanResult!['ml_insights'] ?? {};

    return Column(
      children: [
        _buildGauge(riskScore, theme),
        const SizedBox(height: 20),
        _buildSummaryCard(theme, overallStatus, userTip),
        const SizedBox(height: 20),
        _buildMlInsightsCard(theme, mlInsights),
        const SizedBox(height: 20),
        _buildReputationCard(theme, reputation),
        const SizedBox(height: 20),
        _buildDomainInfoCard(theme, domainAnalysis),
        const SizedBox(height: 20),
        _buildNetworkCard(theme, network),
        const SizedBox(height: 20),
        _buildVisualCard(theme, visual),
      ],
    );
  }

  // --- All helper widgets below have been updated or added ---
  Widget _buildGauge(int riskScore, ThemeData theme) {
    Color riskColor;
    if (riskScore >= 75) riskColor = const Color(0xFFFF4747);
    else if (riskScore >= 50) riskColor = Colors.orange[600]!;
    else if (riskScore >= 25) riskColor = Colors.yellow[600]!;
    else riskColor = theme.primaryColor;
    return SizedBox(
      height: 200,
      child: SfRadialGauge(
        axes: <RadialAxis>[
          RadialAxis(
            minimum: 0, maximum: 100, showLabels: false, showTicks: false,
            axisLineStyle: const AxisLineStyle(thickness: 0.2, cornerStyle: CornerStyle.bothCurve, color: Colors.black26, thicknessUnit: GaugeSizeUnit.factor),
            pointers: <GaugePointer>[RangePointer(value: riskScore.toDouble(), cornerStyle: CornerStyle.bothCurve, width: 0.2, sizeUnit: GaugeSizeUnit.factor, color: riskColor)],
            annotations: <GaugeAnnotation>[
              GaugeAnnotation(
                widget: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text("$riskScore%", style: theme.textTheme.displaySmall?.copyWith(fontWeight: FontWeight.bold, color: riskColor)),
                    Text("Risk Score", style: theme.textTheme.bodyLarge?.copyWith(color: Colors.grey[400])),
                  ],
                ),
                angle: 90, positionFactor: 0.1,
              )
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryCard(ThemeData theme, String status, String tip) {
    final statusColor = status.toLowerCase().contains('risky') || status.toLowerCase().contains('malicious')
        ? Colors.red[400]
        : status.toLowerCase().contains('suspicious')
        ? Colors.orange[600]
        : theme.primaryColor;
    return _buildSectionCard(
      theme: theme, title: "Scan Summary", icon: Icons.shield_moon_outlined,
      children: [
        Text(status.toUpperCase(), style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: statusColor, letterSpacing: 1)),
        const SizedBox(height: 8),
        Text(tip, style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey[300])),
      ],
    );
  }

  Widget _buildMlInsightsCard(ThemeData theme, Map<String, dynamic> insights) {
    List<String> indicators = List<String>.from(insights['top_risk_indicators'] ?? []);
    return _buildSectionCard(
      theme: theme, title: "ML Insights", icon: Icons.auto_awesome,
      children: [
        Text("Top Risk Indicators:", style: TextStyle(color: Colors.grey[400])),
        const SizedBox(height: 8),
        if (indicators.isEmpty)
          const Text("• None detected", style: TextStyle(color: Colors.white))
        else
          ...indicators.map((indicator) => Text("• $indicator", style: const TextStyle(color: Colors.white))),
      ],
    );
  }

  Widget _buildReputationCard(ThemeData theme, Map<String, dynamic> reputation) {
    int positives = reputation['virustotal_positives'] ?? 0;
    int total = reputation['virustotal_total'] ?? 0;
    bool onBlacklist = reputation['is_on_blacklist'] ?? false;
    bool isGsBThreat = reputation['google_safe_browsing']?['is_threat'] ?? false;
    return _buildSectionCard(
      theme: theme, title: "Reputation", icon: Icons.verified_user_outlined,
      children: [
        _buildInfoRow(theme, "VirusTotal Detections", "$positives / $total", positives > 0 ? const Color(0xFFFF4747) : theme.primaryColor),
        _buildInfoRow(theme, "Google Safe Browsing", isGsBThreat ? "Threat" : "Clean", isGsBThreat ? const Color(0xFFFF4747) : theme.primaryColor),
        _buildInfoRow(theme, "On Blacklist", onBlacklist ? "Yes" : "No", onBlacklist ? const Color(0xFFFF4747) : theme.primaryColor),
      ],
    );
  }

  Widget _buildDomainInfoCard(ThemeData theme, Map<String, dynamic> domain) {
    int age = domain['domain_age_days'] ?? -1;
    bool hasSSL = domain['has_ssl'] == 1;
    return _buildSectionCard(
      theme: theme, title: "Domain Info", icon: Icons.language,
      children: [
        _buildInfoRow(theme, "Domain Age", age == -1 ? "Unknown" : "$age days", age > 365 ? theme.primaryColor : Colors.yellow[600]!),
        _buildInfoRow(theme, "SSL Certificate", hasSSL ? "Active" : "Missing", hasSSL ? theme.primaryColor : const Color(0xFFFF4747)),
      ],
    );
  }

  Widget _buildNetworkCard(ThemeData theme, Map<String, dynamic> network) {
    var headers = network['has_security_headers'] ?? {};
    bool hasCsp = headers['csp'] ?? false;
    bool hasHsts = headers['hsts'] ?? false;
    return _buildSectionCard(
      theme: theme, title: "Network Security", icon: Icons.router_outlined,
      children: [
        _buildInfoRow(theme, "Content Security Policy (CSP)", hasCsp ? "Yes" : "No", hasCsp ? theme.primaryColor : Colors.yellow[600]!),
        _buildInfoRow(theme, "Strict Transport Security (HSTS)", hasHsts ? "Yes" : "No", hasHsts ? theme.primaryColor : Colors.yellow[600]!),
      ],
    );
  }

  Widget _buildVisualCard(ThemeData theme, Map<String, dynamic> visual) {
    bool impersonation = visual['brand_impersonation_detected'] ?? false;
    String brand = visual['suspected_brand'] ?? 'N/A';
    return _buildSectionCard(
      theme: theme, title: "Visual Analysis", icon: Icons.remove_red_eye_outlined,
      children: [
        _buildInfoRow(theme, "Brand Impersonation", impersonation ? "Detected ($brand)" : "None", impersonation ? const Color(0xFFFF4747) : theme.primaryColor),
      ],
    );
  }

  Widget _buildSectionCard({required ThemeData theme, required String title, required IconData icon, required List<Widget> children}) {
    return GlassmorphicCard(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: theme.primaryColor),
                const SizedBox(width: 8),
                Text(title, style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            Divider(color: Colors.grey[800], height: 24),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(ThemeData theme, String title, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(child: Text(title, style: TextStyle(color: Colors.grey[400]), overflow: TextOverflow.ellipsis)),
          Text(value, style: TextStyle(color: valueColor, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
