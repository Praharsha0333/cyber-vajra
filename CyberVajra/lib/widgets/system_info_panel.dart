import 'package:flutter/material.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'dart:async';
import 'dart:io';

class SystemInfoPanel extends StatefulWidget {
  const SystemInfoPanel({super.key});

  @override
  State<SystemInfoPanel> createState() => _SystemInfoPanelState();
}

class _SystemInfoPanelState extends State<SystemInfoPanel> {
  String _connectionStatus = "Unknown";
  String _ipAddress = "Fetching...";
  late StreamSubscription<List<ConnectivityResult>> _subscription;

  @override
  void initState() {
    super.initState();

    // Listen to connectivity changes
    _subscription = Connectivity()
        .onConnectivityChanged
        .listen((List<ConnectivityResult> results) {
      if (results.isNotEmpty) {
        final result = results.first;
        setState(() {
          _connectionStatus =
          result == ConnectivityResult.mobile ? "Mobile Data" : "Wi-Fi";
        });
        _getIPAddress();
      }
    });
  }

  // Get IP Address
  Future<void> _getIPAddress() async {
    try {
      final interfaces = await NetworkInterface.list(
        type: InternetAddressType.IPv4,
        includeLoopback: false,
      );
      if (interfaces.isNotEmpty && interfaces.first.addresses.isNotEmpty) {
        setState(() {
          _ipAddress = interfaces.first.addresses.first.address;
        });
      } else {
        setState(() {
          _ipAddress = "Unavailable";
        });
      }
    } catch (e) {
      setState(() {
        _ipAddress = "Error";
      });
    }
  }

  @override
  void dispose() {
    _subscription.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        const Icon(Icons.wifi, size: 50, color: Colors.greenAccent),
        const SizedBox(height: 10),
        Text(
          "Connection: $_connectionStatus",
          style: const TextStyle(color: Colors.white, fontSize: 16),
        ),
        Text(
          "IP Address: $_ipAddress",
          style: const TextStyle(color: Colors.white, fontSize: 16),
        ),
      ],
    );
  }
}
