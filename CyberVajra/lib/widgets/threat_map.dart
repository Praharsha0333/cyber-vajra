import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../services/AbuseIPDB_api.dart';
import '../other/country_coords.dart';

class ThreatMap extends StatefulWidget {
  final ThreatDataApi api;
  const ThreatMap({super.key, required this.api});

  @override
  State<ThreatMap> createState() => _ThreatMapState();
}

class _ThreatMapState extends State<ThreatMap> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  List<AbuseIpRecord> _threats = [];

  @override
  void initState() {
    super.initState();
    _controller =
    AnimationController(vsync: this, duration: const Duration(seconds: 2))
      ..repeat();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final data = await widget.api.fetchBlacklist();
      if (mounted) {
        setState(() => _threats = data);
      }
    } catch (e) {
      debugPrint("Error fetching threat blacklist: $e");
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // --- FIX: Wrap the widget in an AspectRatio to enforce the map's 2:1 shape ---
    // This ensures the map is never cropped and the coordinate projection is always correct.
    return AspectRatio(
      aspectRatio: 2 / 1,
      child: Stack(
        children: [
          // Background world map
          // --- FIX: Use BoxFit.fill to stretch the map to the container's edges ---
          // Since the AspectRatio is correct, this will not cause distortion.
          SvgPicture.asset(
            "assets/world_map.svg",
            fit: BoxFit.fill,
          ),

          // Overlay: animated threat heatmap
          AnimatedBuilder(
            animation: _controller,
            builder: (_, __) => CustomPaint(
              painter: _ThreatPainter(_threats, _controller.value),
              size: Size.infinite,
            ),
          ),
        ],
      ),
    );
  }
}

/// Painter for pulsing threat circles
class _ThreatPainter extends CustomPainter {
  final List<AbuseIpRecord> threats;
  final double progress;

  _ThreatPainter(this.threats, this.progress);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();

    for (final record in threats) {
      final coords = countryCoords[record.countryCode];
      if (coords == null) continue;

      final center = _project(coords[0], coords[1], size);

      if (record.abuseConfidenceScore == 100) {
        paint.color = Colors.red.withOpacity(0.8);
      } else if (record.abuseConfidenceScore > 75) {
        paint.color = Colors.orange.withOpacity(0.7);
      } else {
        paint.color = Colors.yellow.withOpacity(0.6);
      }

      final easedProgress = Curves.easeInOut.transform(progress);
      final pulse = math.sin(easedProgress * 2 * math.pi);
      final radius = 5 + (record.abuseConfidenceScore / 10) * (0.5 + 0.5 * pulse);

      canvas.drawCircle(center, radius, paint);
    }
  }

  // Projects latitude and longitude to screen coordinates
  Offset _project(double lat, double lon, Size size) {
    final x = (lon + 180) / 360 * size.width;
    final y = (90 - lat) / 180 * size.height;
    return Offset(x, y);
  }

  @override
  bool shouldRepaint(covariant _ThreatPainter oldDelegate) => true;
}
