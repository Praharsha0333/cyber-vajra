import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import './glassmorphic_card.dart';

/// A circular pie chart to display the ratio of safe scans to threats found.
class StatisticsChart extends StatelessWidget {
  final int safeCount;
  final int suspiciousCount;

  const StatisticsChart({
    super.key,
    required this.safeCount,
    required this.suspiciousCount,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final totalScans = safeCount + suspiciousCount;

    return GlassmorphicCard(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Text("Scan Statistics",
                style: theme.textTheme.titleLarge
                    ?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            SizedBox(
              height: 150,
              child: Stack(
                children: [
                  PieChart(
                    PieChartData(
                      startDegreeOffset: 180,
                      sections: _buildChartSections(theme),
                      centerSpaceRadius: 50,
                      sectionsSpace: 2,
                      pieTouchData: PieTouchData(enabled: false),
                    ),
                    swapAnimationDuration: const Duration(milliseconds: 750),
                    swapAnimationCurve: Curves.easeInOutQuint,
                  ),
                  Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          "$totalScans",
                          style: theme.textTheme.headlineMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        Text("Total Scans",
                            style: TextStyle(color: Colors.grey[400])),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildLegendItem(theme.primaryColor, "Safe Scans"),
                const SizedBox(width: 24),
                _buildLegendItem(const Color(0xFFFF4747), "Threats Found"),
              ],
            ),
          ],
        ),
      ),
    );
  }

  List<PieChartSectionData> _buildChartSections(ThemeData theme) {
    final isNotEmpty = safeCount > 0 || suspiciousCount > 0;
    if (!isNotEmpty) {
      return [
        PieChartSectionData(
          value: 1,
          color: Colors.grey[800],
          title: "",
          radius: 25,
        ),
      ];
    }
    return [
      PieChartSectionData(
        value: safeCount.toDouble(),
        color: theme.primaryColor,
        title: "",
        radius: 25,
      ),
      PieChartSectionData(
        value: suspiciousCount.toDouble(),
        color: const Color(0xFFFF4747),
        title: "",
        radius: 25,
      ),
    ];
  }

  Widget _buildLegendItem(Color color, String text) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
              color: color,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.5),
                  blurRadius: 4,
                )
              ]),
        ),
        const SizedBox(width: 8),
        Text(text, style: TextStyle(color: Colors.grey[300])),
      ],
    );
  }
}

