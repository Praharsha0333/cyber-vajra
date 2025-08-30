import 'dart:async';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/splash_screen.dart';
import 'screens/screen_dashboard.dart';
import 'screens/screen_globaldata.dart';
import 'screens/screen_learn.dart';
import 'screens/screen_report.dart';

void main() {
  runApp(const CyberGuardApp());
}

class CyberGuardApp extends StatelessWidget {
  const CyberGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    const primaryColor = Color(0xFF00FFAB);
    const backgroundColor = Color(0xFF0A0A0A);

    final neonTheme = ThemeData.dark().copyWith(
      scaffoldBackgroundColor: backgroundColor,
      primaryColor: primaryColor,
      textTheme: GoogleFonts.robotoMonoTextTheme(ThemeData.dark().textTheme),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.black,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
          elevation: 8,
        ),
      ),
      iconTheme: const IconThemeData(color: primaryColor, size: 24),
      cardTheme: const CardThemeData(color: Colors.transparent, elevation: 0),
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: neonTheme,
      home: const SplashScreen(), // Splash first
    );
  }
}

/// After splash → goes here
class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    DashboardScreen(),
    GlobalDataScreen(),
    LearnScreen(),
    ReportScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_currentIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
        type: BottomNavigationBarType.fixed,
        selectedItemColor: Theme.of(context).primaryColor,
        unselectedItemColor: Colors.grey,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard), label: "Dashboard"),
          BottomNavigationBarItem(icon: Icon(Icons.public), label: "Global Data"),
          BottomNavigationBarItem(icon: Icon(Icons.school), label: "Learn"),
          BottomNavigationBarItem(icon: Icon(Icons.report), label: "Report"),
        ],
      ),
    );
  }
}
