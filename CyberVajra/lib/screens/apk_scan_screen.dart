import 'dart:io';
import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:file_picker/file_picker.dart';
import 'package:syncfusion_flutter_gauges/gauges.dart';
import '../services/api_service.dart'; // Make sure this path is correct
import '../widgets/scanning_animation.dart';

// (You should move the real GlassmorphicCard widget to its own file)
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


class ApkScanScreen extends StatefulWidget {
  final Function(bool suspicious, String log)? onScanComplete;

  const ApkScanScreen({super.key, this.onScanComplete});

  @override
  State<ApkScanScreen> createState() => _ApkScanScreenState();
}

class _ApkScanScreenState extends State<ApkScanScreen> {
  // --- LOGIC SECTION ---
  File? _selectedFile;
  bool _loading = false;
  Map<String, dynamic>? _scanResult;

  Future<void> _pickFile() async {
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ["apk"],
    );
    if (result != null && result.files.single.path != null) {
      setState(() {
        _selectedFile = File(result.files.single.path!);
        _scanResult = null;
      });
    }
  }

  Future<void> _scanApk() async {
    if (_selectedFile == null) return;

    setState(() {
      _loading = true;
      _scanResult = null;
    });

    final stopwatch = Stopwatch()..start();

    var result = await ApiService.scanApk(_selectedFile!);

    stopwatch.stop();

    final remainingTime = const Duration(seconds: 5) - stopwatch.elapsed;
    if (remainingTime > Duration.zero) {
      await Future.delayed(remainingTime);
    }

    setState(() {
      _loading = false;
      _scanResult = result;
    });

    if (widget.onScanComplete != null && result['error'] == null) {
      int riskScore = result['details']?['risk_score'] ?? 0;
      bool suspicious = riskScore > 50;
      String fileName = _selectedFile!.path.split('/').last;
      String log = suspicious
          ? "High risk found in $fileName ($riskScore%)"
          : "Scanned $fileName, looks safe.";
      widget.onScanComplete!(suspicious, log);
    }
  }
  // --- END OF LOGIC SECTION ---

  // --- WIDGET BUILDERS ---

  Widget _buildGauge(int riskScore, ThemeData theme) {
    Color riskColor;
    if (riskScore >= 80) {
      riskColor = const Color(0xFFFF4747); // Neon Red
    } else if (riskScore >= 60) {
      riskColor = Colors.orange[600]!;
    } else if (riskScore >= 40) {
      riskColor = Colors.yellow[600]!;
    } else if (riskScore >= 20) {
      riskColor = Colors.lightGreenAccent[400]!;
    } else {
      riskColor = theme.primaryColor; // Neon Green
    }
    return SizedBox(
      height: 220,
      child: SfRadialGauge(
        axes: <RadialAxis>[
          RadialAxis(
            minimum: 0,
            maximum: 100,
            showLabels: false,
            showTicks: false,
            axisLineStyle: const AxisLineStyle(
              thickness: 0.2,
              cornerStyle: CornerStyle.bothCurve,
              color: Colors.black26,
              thicknessUnit: GaugeSizeUnit.factor,
            ),
            pointers: <GaugePointer>[
              RangePointer(
                value: riskScore.toDouble(),
                cornerStyle: CornerStyle.bothCurve,
                width: 0.2,
                sizeUnit: GaugeSizeUnit.factor,
                color: riskColor,
                gradient: SweepGradient(
                  colors: <Color>[riskColor.withOpacity(0.5), riskColor],
                  stops: const <double>[0.25, 0.9],
                ),
              ),
            ],
            annotations: <GaugeAnnotation>[
              GaugeAnnotation(
                widget: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "$riskScore%",
                      style: theme.textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: riskColor,
                        shadows: [
                          Shadow(blurRadius: 10.0, color: riskColor.withOpacity(0.7)),
                        ],
                      ),
                    ),
                    Text(
                      "Risk Score",
                      style: theme.textTheme.bodyLarge?.copyWith(color: Colors.grey[400]),
                    )
                  ],
                ),
                angle: 90,
                positionFactor: 0.1,
              )
            ],
          )
        ],
      ),
    );
  }

  Widget _buildResult(ThemeData theme) {
    if (_scanResult == null) return const SizedBox();
    if (_scanResult!['error'] != null) {
      return Text("Error: ${_scanResult!['error']}", style: TextStyle(color: Colors.red[400]));
    }

    var details = _scanResult!['details'] ?? {};
    int riskScore = details['risk_score'] ?? 0;
    String confidenceLevel = _scanResult!['confidence_level'] ?? 'Unknown';
    var aiAnalysis = details['ai_analysis'] ?? {};
    String classification = aiAnalysis['type'] ?? 'Unknown';
    var metadata = details['metadata'] ?? {};
    var virustotal = details['virustotal'] ?? {};
    var reasons = _scanResult!['reasons'] as List? ?? [];
    var permissions = metadata['permissions'] as List? ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Center(child: _buildGauge(riskScore, theme)),
        const SizedBox(height: 20),

        _buildSectionCard(
          theme: theme,
          title: "Confidence Level",
          icon: Icons.shield_moon_outlined,
          children: [
            Text(confidenceLevel, style: theme.textTheme.titleLarge?.copyWith(color: Colors.white)),
          ],
        ),
        const SizedBox(height: 20),

        _buildSectionCard(
          theme: theme,
          title: "AI Classification",
          icon: Icons.auto_awesome,
          children: [
            Text(classification, style: theme.textTheme.titleLarge?.copyWith(color: Colors.white)),
          ],
        ),
        const SizedBox(height: 20),

        if (virustotal['total'] != null) ...[
          _buildVirusTotalCard(theme, virustotal),
          const SizedBox(height: 20),
        ],

        if (reasons.isNotEmpty) ...[
          _buildSectionCard(
            theme: theme,
            title: "Risks Detected",
            icon: Icons.warning_amber_rounded,
            children: reasons.map<Widget>((r) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(r['risk_type'] ?? 'Unknown Risk', style: TextStyle(color: Colors.red[300], fontWeight: FontWeight.bold)),
                    const SizedBox(height: 4),
                    Text("• ${r['message'] ?? 'No details'}", style: theme.textTheme.bodyMedium),
                  ],
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 20),
        ],

        if (permissions.isNotEmpty) ...[
          _buildPermissionsCard(theme, permissions),
          const SizedBox(height: 20),
        ],

        _buildSectionCard(
          theme: theme,
          title: "App Metadata",
          icon: Icons.inventory_2_outlined,
          children: [
            _buildMetadataRow(theme, "App Name", metadata['app_name']),
            _buildMetadataRow(theme, "Package", metadata['package_name']),
            _buildMetadataRow(theme, "Version", metadata['version_name']),
            _buildMetadataRow(theme, "File SHA256", metadata['file_sha256'], isHash: true),
            _buildMetadataRow(theme, "Signature", metadata['signature_sha256'], isHash: true),
          ],
        ),
      ],
    );
  }

  // --- HELPER WIDGETS ---
  Widget _buildVirusTotalCard(ThemeData theme, Map<String, dynamic> virustotal) {
    int positives = virustotal['positives'] ?? 0;
    int total = virustotal['total'] ?? 0;
    Color scoreColor = positives > 0 ? const Color(0xFFFF4747) : theme.primaryColor;

    return _buildSectionCard(
      theme: theme,
      title: "VirusTotal Score",
      icon: Icons.verified_user_outlined,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.baseline,
          textBaseline: TextBaseline.alphabetic,
          children: [
            Text("$positives", style: theme.textTheme.displaySmall?.copyWith(color: scoreColor, fontWeight: FontWeight.bold)),
            Text(" / $total", style: theme.textTheme.titleLarge?.copyWith(color: Colors.grey[400])),
          ],
        ),
        const SizedBox(height: 4),
        Center(child: Text("vendors flagged this file as malicious", style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey[400]))),
      ],
    );
  }

  Widget _buildPermissionsCard(ThemeData theme, List permissions) {
    return GlassmorphicCard(
      child: ExpansionTile(
        title: Row(
          children: [
            Icon(Icons.key, color: theme.primaryColor),
            const SizedBox(width: 8),
            Text("App Permissions (${permissions.length})", style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
          ],
        ),
        childrenPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        expandedCrossAxisAlignment: CrossAxisAlignment.start,
        iconColor: Colors.white,
        collapsedIconColor: Colors.white,
        children: permissions.map<Widget>((p) {
          final permissionName = p.toString().split('.').last;
          return Padding(
            padding: const EdgeInsets.only(bottom: 8.0),
            child: Text("• $permissionName", style: theme.textTheme.bodyMedium?.copyWith(color: Colors.grey[300])),
          );
        }).toList(),
      ),
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

  Widget _buildMetadataRow(ThemeData theme, String title, String? value, {bool isHash = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("$title: ", style: TextStyle(color: Colors.grey[400])),
          Expanded(
            child: InkWell(
              onTap: isHash ? () {
                Clipboard.setData(ClipboardData(text: value ?? ''));
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Copied to clipboard')),
                );
              } : null,
              child: Text(
                value ?? 'N/A',
                style: TextStyle(color: Colors.white, overflow: isHash ? TextOverflow.ellipsis : null),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text("APK Scanner", style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: theme.primaryColor)),
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
                  padding: const EdgeInsets.all(24.0),
                  child: _selectedFile == null
                      ? Column(
                    children: [
                      Icon(Icons.shield_outlined, size: 80, color: theme.primaryColor.withOpacity(0.8)),
                      const SizedBox(height: 20),
                      Text("Ready to Scan", style: theme.textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold)),
                      const SizedBox(height: 8),
                      Text("Select an APK file to check for potential threats.", textAlign: TextAlign.center, style: TextStyle(color: Colors.grey[400])),
                      const SizedBox(height: 24),
                      ElevatedButton.icon(
                        onPressed: _pickFile,
                        icon: const Icon(Icons.upload_file, color: Colors.black),
                        label: const Text("Choose APK"),
                      ),
                    ],
                  )
                      : Column(
                    children: [
                      Text("Selected File:", style: TextStyle(color: Colors.grey[400])),
                      const SizedBox(height: 8),
                      Text(_selectedFile!.path.split('/').last, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 20),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          TextButton(onPressed: _pickFile, child: Text("Change File", style: TextStyle(color: theme.primaryColor))),
                          ElevatedButton(
                            onPressed: _loading ? null : _scanApk,
                            child: const Text("Scan Now"),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 24),

              // --- UPDATE: Custom transition for a better "pop-in" effect ---
              AnimatedSwitcher(
                duration: const Duration(milliseconds: 500),
                transitionBuilder: (Widget child, Animation<double> animation) {
                  return FadeTransition(
                    opacity: animation,
                    child: ScaleTransition(
                      scale: animation,
                      child: child,
                    ),
                  );
                },
                child: _loading
                    ? Padding(
                  // Add a key to help AnimatedSwitcher identify the widget
                  key: const ValueKey('loading'),
                  padding: const EdgeInsets.symmetric(vertical: 40.0),
                  child: const ScanningAnimation(),
                )
                    : _scanResult != null
                // Add a key here as well
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
}

