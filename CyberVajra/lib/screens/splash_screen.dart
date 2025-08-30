import 'dart:async';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../main.dart'; // This should point to the file with MainNavigation

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with TickerProviderStateMixin {
  late AnimationController _liquidController;
  late Animation<double> _liquidRadiusAnimation;
  late Animation<double> _liquidWaveAnimation;

  late AnimationController _fadeController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();

    // Controller for the liquid reveal animation
    _liquidController = AnimationController(
      duration: const Duration(milliseconds: 2000),
      vsync: this,
    );

    // Animate the radius of the liquid circle
    _liquidRadiusAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _liquidController, curve: Curves.easeOutQuart),
    );
    // Animate the waviness of the liquid circle
    _liquidWaveAnimation = Tween<double>(begin: 0.0, end: 2 * pi).animate(
      CurvedAnimation(parent: _liquidController, curve: Curves.easeInOut),
    );

    // Controller for the fade-in animation of the content
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _fadeAnimation = CurvedAnimation(
      parent: _fadeController,
      curve: Curves.easeIn,
    );

    // Start animations
    _liquidController.forward();
    Timer(const Duration(milliseconds: 800), () => _fadeController.forward());

    // Navigate to the main app after a delay
    Timer(const Duration(seconds: 4), () {
      if (mounted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const MainNavigation()),
        );
      }
    });
  }

  @override
  void dispose() {
    _liquidController.dispose();
    _fadeController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const Color lightBlue = Color(0xFFE3F2FD);
    const Color darkBlue = Color(0xFF0D47A1);
    final screenSize = MediaQuery.of(context).size;
    final maxRadius = sqrt(pow(screenSize.width, 2) + pow(screenSize.height, 2));

    return Scaffold(
      backgroundColor: lightBlue,
      body: Stack(
        alignment: Alignment.center,
        children: [
          // The animated liquid reveal
          AnimatedBuilder(
            animation: _liquidController,
            builder: (context, child) {
              return ClipPath(
                clipper: LiquidCircleClipper(
                  radius: _liquidRadiusAnimation.value * maxRadius,
                  wavePhase: _liquidWaveAnimation.value,
                ),
                child: Container(color: darkBlue),
              );
            },
          ),

          // The content that fades in
          FadeTransition(
            opacity: _fadeAnimation,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(flex: 3),
                Container(
                  width: 220, // Increased from 200
                  height: 220, // Increased from 200
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black26,
                        blurRadius: 20,
                        offset: Offset(0, 4),
                      )
                    ],
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Image.asset(
                          'assets/logo.png',
                          width: 120,
                          height: 120,
                        ),
                        const SizedBox(height: 8),
                        _buildMadeInIndiaBanner(darkBlue),
                      ],
                    ),
                  ),
                ),
                const Spacer(flex: 2),
                Text(
                  "Version 1.0",
                  style: TextStyle(color: lightBlue.withOpacity(0.8), fontSize: 12),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMadeInIndiaBanner(Color textColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // --- UPDATE: Replaced the '=' symbols with the Indian Flag Emoji ---
        const Text('🇮🇳', style: TextStyle(fontSize: 16)),
        const SizedBox(width: 8),
        Text(
          "Made by India",
          style: GoogleFonts.lato(
            color: textColor,
            fontWeight: FontWeight.bold,
            fontSize: 15,
          ),
        ),
        const SizedBox(width: 8),
        const Text('🇮🇳', style: TextStyle(fontSize: 16)),
      ],
    );
  }
}

/// A custom clipper that creates an expanding circle with a wavy, liquid-like edge.
class LiquidCircleClipper extends CustomClipper<Path> {
  final double radius;
  final double wavePhase;

  LiquidCircleClipper({required this.radius, required this.wavePhase});

  @override
  Path getClip(Size size) {
    final path = Path();
    final center = Offset(size.width / 2, size.height / 2);
    const waveAmplitude = 15.0; // How wavy the edge is
    const waveFrequency = 6; // How many waves are around the circle

    for (int i = 0; i <= 360; i++) {
      final angle = i * pi / 180;
      final currentRadius = radius + sin(angle * waveFrequency + wavePhase) * waveAmplitude;
      final x = center.dx + currentRadius * cos(angle);
      final y = center.dy + currentRadius * sin(angle);
      if (i == 0) {
        path.moveTo(x, y);
      } else {
        path.lineTo(x, y);
      }
    }
    path.close();
    return path;
  }

  @override
  bool shouldReclip(CustomClipper<Path> oldClipper) => true;
}

