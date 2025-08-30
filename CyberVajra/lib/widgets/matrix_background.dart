import 'dart:math';
import 'package:flutter/material.dart';

class MatrixBackground extends StatefulWidget {
  @override
  _MatrixBackgroundState createState() => _MatrixBackgroundState();
}

class _MatrixBackgroundState extends State<MatrixBackground>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  final random = Random();
  final List<String> chars = ['0', '1', '#', '\$', '%', '&'];

  @override
  void initState() {
    super.initState();
    _controller =
    AnimationController(vsync: this, duration: Duration(seconds: 20))
      ..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) {
        return CustomPaint(
          painter: MatrixPainter(_controller.value, chars),
          size: Size.infinite,
        );
      },
    );
  }
}

class MatrixPainter extends CustomPainter {
  final double progress;
  final List<String> chars;
  final Random random = Random();

  MatrixPainter(this.progress, this.chars);

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint();
    final textStyle = TextStyle(
      color: Colors.greenAccent.withOpacity(0.8),
      fontSize: 16,
      fontFamily: 'monospace',
    );

    final columnWidth = 20;
    final rowHeight = 20;

    for (int x = 0; x < size.width / columnWidth; x++) {
      for (int y = 0; y < size.height / rowHeight; y++) {
        if (random.nextDouble() < 0.02) {
          final textSpan = TextSpan(
            text: chars[random.nextInt(chars.length)],
            style: textStyle,
          );
          final tp = TextPainter(
            text: textSpan,
            textAlign: TextAlign.center,
            textDirection: TextDirection.ltr,
          );
          tp.layout();
          tp.paint(
              canvas,
              Offset(x * columnWidth.toDouble(),
                  (y * rowHeight.toDouble() + progress * size.height) %
                      size.height));
        }
      }
    }
  }

  @override
  bool shouldRepaint(CustomPainter oldDelegate) => true;
}
