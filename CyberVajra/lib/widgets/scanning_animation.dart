import 'dart:math';
import 'dart:ui';
import 'package:flutter/material.dart';

class ScanningAnimation extends StatefulWidget {
  final double width;
  final double height;

  const ScanningAnimation({
    super.key,
    this.width = double.infinity,
    this.height = 250,
  });

  @override
  State<ScanningAnimation> createState() => _ScanningAnimationState();
}

class _ScanningAnimationState extends State<ScanningAnimation>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 4), // A slightly longer, smoother scan
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: widget.width,
      height: widget.height,
      child: Stack(
        alignment: Alignment.center,
        children: [
          AnimatedBuilder(
            animation: _controller,
            builder: (context, child) {
              return CustomPaint(
                size: Size(widget.width, widget.height),
                painter: _ScannerPainter(
                  progress: _controller.value,
                  scanColor: Colors.cyanAccent,
                ),
              );
            },
          ),
          Text(
            "ANALYZING...",
            style: TextStyle(
              color: Colors.cyanAccent.withOpacity(0.8),
              fontSize: 18,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
              shadows: [
                Shadow(
                  blurRadius: 10.0,
                  color: Colors.cyanAccent,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// --- UPDATE: Redesigned painter for a left-to-right random wave scan ---
class _ScannerPainter extends CustomPainter {
  final double progress;
  final Color scanColor;
  final Random _random = Random();

  _ScannerPainter({required this.progress, required this.scanColor});

  @override
  void paint(Canvas canvas, Size size) {
    // 1. Paint the background grid
    _paintGrid(canvas, size);

    // 2. Define the wave path
    final wavePath = _createWavePath(size);

    // 3. Define the fill path beneath the wave
    final fillPath = _createFillPath(wavePath, size);

    // 4. Calculate the clipping rectangle based on progress
    final clipRect = Rect.fromLTRB(0, 0, size.width * progress, size.height);
    canvas.save();
    canvas.clipRect(clipRect);

    // 5. Paint the fill and the wave inside the clipped area
    _paintFill(canvas, fillPath);
    _paintWave(canvas, wavePath);

    canvas.restore();
  }

  void _paintGrid(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.1)
      ..strokeWidth = 0.5;

    const double spacing = 20.0;
    for (double i = 0; i < size.width; i += spacing) {
      canvas.drawLine(Offset(i, 0), Offset(i, size.height), paint);
    }
    for (double i = 0; i < size.height; i += spacing) {
      canvas.drawLine(Offset(0, i), Offset(size.width, i), paint);
    }
  }

  Path _createWavePath(Size size) {
    final path = Path();
    final middleY = size.height / 2;
    path.moveTo(0, middleY);

    for (double i = 0; i <= size.width; i++) {
      final sine1 = sin(i * 0.02 + progress * pi);
      final sine2 = sin(i * 0.05 + progress * 2 * pi);
      final jitter = (_random.nextDouble() - 0.5) * 20;

      final y = middleY +
          (sine1 * size.height * 0.2) +
          (sine2 * size.height * 0.1) +
          jitter;

      path.lineTo(i, y.clamp(0.0, size.height)); // Clamp to stay within bounds
    }
    return path;
  }

  Path _createFillPath(Path wavePath, Size size) {
    final fillPath = Path.from(wavePath);
    fillPath.lineTo(size.width, size.height);
    fillPath.lineTo(0, size.height);
    fillPath.close();
    return fillPath;
  }

  void _paintFill(Canvas canvas, Path fillPath) {
    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [scanColor.withOpacity(0.3), scanColor.withOpacity(0.01)],
      ).createShader(Rect.fromLTWH(0, 0, 500, 250)); // Dummy size, shader will fill the path area
    canvas.drawPath(fillPath, fillPaint);
  }

  void _paintWave(Canvas canvas, Path wavePath) {
    final wavePaint = Paint()
      ..color = scanColor
      ..strokeWidth = 2.0
      ..style = PaintingStyle.stroke
      ..shader = LinearGradient(
        colors: [scanColor.withOpacity(0.5), scanColor],
      ).createShader(Rect.fromLTWH(0, 0, 500, 250));
    canvas.drawPath(wavePath, wavePaint);
  }

  @override
  bool shouldRepaint(covariant _ScannerPainter oldDelegate) {
    return progress != oldDelegate.progress;
  }
}

