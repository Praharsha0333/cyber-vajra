import 'dart:math';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/AbuseIPDB_api.dart';

/// A widget that displays a visually appealing, interactive 3D globe
/// with a world map texture and animated arcs representing cyber threats.
class GlobalThreatPulse extends StatefulWidget {
  final ThreatDataApi api;

  const GlobalThreatPulse({super.key, required this.api});

  @override
  State<GlobalThreatPulse> createState() => _GlobalThreatPulseState();
}

class _GlobalThreatPulseState extends State<GlobalThreatPulse>
    with TickerProviderStateMixin {
  late AnimationController _rotationController;
  late AnimationController _pulseController;

  Future<List<AbuseIpRecord>>? _threatDataFuture;
  List<_ThreatArc> _arcs = [];
  final Random _random = Random();
  ui.Image? _worldMapImage;

  double _manualRotation = 1.38; // Starts centered on India
  double _startDragX = 0.0;

  static const Map<String, Offset> _countryCoordinates = {
    'US': Offset(38.96, -95.71), 'CN': Offset(35.86, 104.19),
    'RU': Offset(61.52, 105.31), 'DE': Offset(51.16, 10.45),
    'IN': Offset(20.59, 78.96),  'BR': Offset(-14.23, -51.92),
    'GB': Offset(55.37, -3.43),  'AU': Offset(-25.27, 133.77),
    'JP': Offset(36.20, 138.25), 'FR': Offset(46.22, 2.21),
    '??': Offset(0,0),
  };

  @override
  void initState() {
    super.initState();
    _rotationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 40),
    )..repeat();

    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4),
    )..repeat();

    _loadWorldMap();
    _fetchThreatData();
  }

  Future<void> _loadWorldMap() async {
    try {
      final byteData = await rootBundle.load('assets/world_map.png');
      final codec = await ui.instantiateImageCodec(byteData.buffer.asUint8List());
      final frame = await codec.getNextFrame();
      if (mounted) {
        setState(() => _worldMapImage = frame.image);
      }
    } catch (e) {
      debugPrint("Error loading world map image: $e");
    }
  }

  void _fetchThreatData() {
    _threatDataFuture = widget.api.fetchBlacklist();
    _threatDataFuture!.then((data) {
      if (mounted) {
        _generateThreatArcs(data);
      }
    });
  }

  void _generateThreatArcs(List<AbuseIpRecord> records) {
    final destinations = List.from(_countryCoordinates.keys)..shuffle();
    _arcs = records.map((record) {
      final start = _countryCoordinates[record.countryCode] ?? _countryCoordinates['??'];
      final end = _countryCoordinates[destinations.firstWhere((d) => d != record.countryCode, orElse: () => 'US')];

      if (start != null && end != null) {
        return _ThreatArc(start: start, end: end, startTime: _random.nextDouble());
      }
      return null;
    }).where((arc) => arc != null).cast<_ThreatArc>().toList();
  }

  void _onPanStart(DragStartDetails details) {
    _startDragX = details.globalPosition.dx;
  }

  void _onPanUpdate(DragUpdateDetails details) {
    final dx = details.globalPosition.dx - _startDragX;
    setState(() {
      _manualRotation += dx * 0.005;
    });
    _startDragX = details.globalPosition.dx;
  }

  @override
  void dispose() {
    _rotationController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onPanStart: _onPanStart,
      onPanUpdate: _onPanUpdate,
      child: FutureBuilder<List<AbuseIpRecord>>(
        future: _threatDataFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error fetching threat data.', style: TextStyle(color: Colors.red[300])));
          } else if (snapshot.hasData && _worldMapImage != null) {
            return AnimatedBuilder(
              animation: Listenable.merge([_rotationController, _pulseController]),
              builder: (context, child) {
                return CustomPaint(
                  size: const Size(double.infinity, 300),
                  painter: _GlobePainter(
                    rotation: (_rotationController.value * 2 * pi) + _manualRotation,
                    pulseProgress: _pulseController.value,
                    arcs: _arcs,
                    mapImage: _worldMapImage!,
                    themeColor: Theme.of(context).primaryColor, // Pass theme color
                  ),
                );
              },
            );
          }
          return Center(child: Text("Loading Map...", style: TextStyle(color: Colors.grey[400])));
        },
      ),
    );
  }
}

class _GlobePainter extends CustomPainter {
  final double rotation;
  final double pulseProgress;
  final List<_ThreatArc> arcs;
  final ui.Image mapImage;
  final Color themeColor;

  _GlobePainter({required this.rotation, required this.pulseProgress, required this.arcs, required this.mapImage, required this.themeColor});

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = min(size.width, size.height) / 2.2;

    _drawGlobeBackground(canvas, center, radius);

    canvas.save();
    canvas.clipPath(Path()..addOval(Rect.fromCircle(center: center, radius: radius)));

    _drawWorldMap(canvas, center, radius);

    for (final arc in arcs) {
      _drawArcAndPulse(canvas, center, radius, arc);
    }

    canvas.restore();
  }

  void _drawGlobeBackground(Canvas canvas, Offset center, double radius) {
    // --- UPDATE: "Holographic Grid" atmosphere ---
    final atmospherePaint = Paint()
      ..shader = ui.Gradient.radial(
        center,
        radius + 15,
        [
          themeColor.withOpacity(0.3),
          themeColor.withOpacity(0.0),
        ],
        [0.8, 1.0],
      );
    canvas.drawCircle(center, radius + 15, atmospherePaint);

    // --- UPDATE: Deep space globe color ---
    final globePaint = Paint()
      ..shader = ui.Gradient.radial(
        center,
        radius,
        [
          const Color(0xFF081828),
          const Color(0xFF000000),
        ],
      );
    canvas.drawCircle(center, radius, globePaint);
  }

  void _drawWorldMap(Canvas canvas, Offset center, double radius) {
    final imageWidth = mapImage.width.toDouble();
    final rotationOffset = (rotation / (2 * pi)) * imageWidth;
    final srcRect1 = Rect.fromLTWH(rotationOffset, 0, imageWidth - rotationOffset, mapImage.height.toDouble());
    final dstRect1 = Rect.fromLTWH(center.dx - radius, center.dy - radius, (imageWidth - rotationOffset) / imageWidth * (2 * radius), 2 * radius);
    final srcRect2 = Rect.fromLTWH(0, 0, rotationOffset, mapImage.height.toDouble());
    final dstRect2 = Rect.fromLTWH(dstRect1.right, center.dy - radius, rotationOffset / imageWidth * (2 * radius), 2 * radius);

    // --- UPDATE: Tint the map's landmasses with the neon theme color ---
    final paint = Paint()
      ..filterQuality = FilterQuality.medium
      ..colorFilter = ColorFilter.mode(
          themeColor.withOpacity(0.5),
          BlendMode.srcATop
      );

    canvas.drawImageRect(mapImage, srcRect1, dstRect1, paint);
    canvas.drawImageRect(mapImage, srcRect2, dstRect2, paint);
  }

  void _drawArcAndPulse(Canvas canvas, Offset center, double radius, _ThreatArc arc) {
    final startPoint = _latLonToPoint(arc.start, center, radius);
    final endPoint = _latLonToPoint(arc.end, center, radius);

    if (startPoint.dx > center.dx - radius && startPoint.dx < center.dx + radius) {
      final controlPoint = Offset(
        (startPoint.dx + endPoint.dx) / 2 + (startPoint.dy - endPoint.dy) * 0.4,
        (startPoint.dy + endPoint.dy) / 2 + (endPoint.dx - startPoint.dx) * 0.4,
      );
      final path = Path()..moveTo(startPoint.dx, startPoint.dy)..quadraticBezierTo(controlPoint.dx, controlPoint.dy, endPoint.dx, endPoint.dy);
      final pathMetrics = path.computeMetrics().first;

      // --- UPDATE: Neon green/cyan trail and pulse colors ---
      final trailPaint = Paint()
        ..color = themeColor.withOpacity(0.25)
        ..strokeWidth = 1.0
        ..style = PaintingStyle.stroke;
      canvas.drawPath(path, trailPaint);

      final pulsePosition = pathMetrics.getTangentForOffset(pathMetrics.length * pulseProgress);
      if (pulsePosition != null) {
        final pulsePaint = Paint()
          ..color = themeColor
          ..maskFilter = const MaskFilter.blur(BlurStyle.normal, 8);
        canvas.drawCircle(pulsePosition.position, 4, pulsePaint);

        final corePaint = Paint()..color = Colors.white;
        canvas.drawCircle(pulsePosition.position, 2, corePaint);
      }
    }
  }

  Offset _latLonToPoint(Offset latLon, Offset center, double radius) {
    final latRad = -latLon.dx * pi / 180;
    final lonRad = latLon.dy * pi / 180;
    final rotatedLon = lonRad - rotation;
    final x = center.dx + radius * cos(latRad) * sin(rotatedLon);
    final y = center.dy + radius * sin(latRad);
    return Offset(x, y);
  }

  @override
  bool shouldRepaint(covariant _GlobePainter oldDelegate) => true;
}

class _ThreatArc {
  final Offset start;
  final Offset end;
  final double startTime;

  _ThreatArc({required this.start, required this.end, required this.startTime});
}

