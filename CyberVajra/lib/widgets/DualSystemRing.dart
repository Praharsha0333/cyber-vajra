import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:system_info2/system_info2.dart';
import 'package:percent_indicator/circular_percent_indicator.dart';

class DualSystemRing extends StatefulWidget {
  @override
  _DualSystemRingState createState() => _DualSystemRingState();
}

class _DualSystemRingState extends State<DualSystemRing> {
  double cpuUsage = 0;
  double memoryUsage = 0;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _fetchStats();
    _timer = Timer.periodic(Duration(seconds: 2), (timer) {
      _fetchStats();
    });
  }

  Future<void> _fetchStats() async {
    try {
      // Memory usage
      int totalMemory = SysInfo.getTotalPhysicalMemory();
      int freeMemory = SysInfo.getFreePhysicalMemory();
      memoryUsage = ((totalMemory - freeMemory) / totalMemory) * 100;

      // CPU usage (platform-specific)
      if (Platform.isWindows) {
        final result =
        await Process.run('wmic', ['cpu', 'get', 'loadpercentage']);
        final lines = result.stdout.toString().trim().split("\n");
        if (lines.length > 1) {
          cpuUsage = double.tryParse(lines[1].trim()) ?? 0;
        }
      } else if (Platform.isLinux) {
        final file = File('/proc/stat');
        final lines = await file.readAsLines();
        final parts = lines.first.split(' ')..removeWhere((p) => p.isEmpty);
        final user = int.parse(parts[1]);
        final nice = int.parse(parts[2]);
        final system = int.parse(parts[3]);
        final idle = int.parse(parts[4]);
        final total = user + nice + system + idle;
        cpuUsage = (1 - (idle / total)) * 100;
      } else {
        cpuUsage = 0; // fallback
      }

      setState(() {});
    } catch (e) {
      print("Error fetching stats: $e");
    }
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Stack(
        alignment: Alignment.center,
        children: [
          CircularPercentIndicator(
            radius: 130.0,
            lineWidth: 13.0,
            percent: memoryUsage / 100,
            progressColor: Colors.blue,
            backgroundColor: Colors.blue.withOpacity(0.1),
            circularStrokeCap: CircularStrokeCap.round,
            center: CircularPercentIndicator(
              radius: 90.0,
              lineWidth: 10.0,
              percent: (cpuUsage / 100).clamp(0.0, 1.0),
              progressColor: Colors.green,
              backgroundColor: Colors.green.withOpacity(0.1),
              circularStrokeCap: CircularStrokeCap.round,
              center: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text("CPU: ${cpuUsage.toStringAsFixed(1)}%",
                      style:
                      TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  Text("RAM: ${memoryUsage.toStringAsFixed(1)}%",
                      style:
                      TextStyle(fontSize: 14, color: Colors.grey[400])),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
