import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

// A modern, styled line chart that fits the CyberGuard theme.
class CyberCrimeLineChart extends StatelessWidget {
  const CyberCrimeLineChart({super.key});

  @override
  Widget build(BuildContext context) {
    // Use the app's primary color for the chart's main elements.
    final primaryColor = Theme.of(context).primaryColor;

    return AspectRatio(
      aspectRatio: 1.7, // Adjust the aspect ratio for better proportions
      child: LineChart(
        LineChartData(
          // --- UI/UX IMPROVEMENT: STYLED GRID ---
          // A subtle grid that doesn't distract from the data line.
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false, // Cleaner look without vertical lines
            getDrawingHorizontalLine: (value) {
              return FlLine(
                color: Colors.grey[850]!, // Softer grid line color
                strokeWidth: 1,
              );
            },
          ),

          // --- UI/UX IMPROVEMENT: CUSTOM TOOLTIPS ---
          // Tooltips that match the app's theme.
          lineTouchData: LineTouchData(
            touchTooltipData: LineTouchTooltipData(
              getTooltipColor: (LineBarSpot spot) => Colors.blueGrey.withOpacity(0.8),
              getTooltipItems: (List<LineBarSpot> touchedBarSpots) {
                return touchedBarSpots.map((barSpot) {
                  return LineTooltipItem(
                    '${barSpot.x.toInt()}: ${barSpot.y.toInt()}K Reports',
                    const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  );
                }).toList();
              },
            ),
          ),

          // --- UI/UX IMPROVEMENT: REFINED TITLES AND BORDERS ---
          titlesData: FlTitlesData(
            show: true,
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 30,
                interval: 1,
                getTitlesWidget: bottomTitleWidgets,
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 20,
                getTitlesWidget: leftTitleWidgets,
                reservedSize: 42,
              ),
            ),
          ),
          borderData: FlBorderData(
            show: false, // Remove the outer border for a cleaner look
          ),
          minX: 2016,
          maxX: 2022,
          minY: 0,
          maxY: 65, // Give some space above the highest point

          // --- UI/UX IMPROVEMENT: STYLED LINE WITH GRADIENT ---
          lineBarsData: [
            LineChartBarData(
              spots: const [
                FlSpot(2016, 20),
                FlSpot(2017, 24),
                FlSpot(2018, 29),
                FlSpot(2019, 43),
                FlSpot(2020, 49),
                FlSpot(2021, 52),
                FlSpot(2022, 62),
              ],
              isCurved: true,
              color: primaryColor, // Use the theme's primary color
              barWidth: 4,
              isStrokeCapRound: true,
              dotData: FlDotData(
                show: true, // Show dots on data points
                getDotPainter: (spot, percent, barData, index) {
                  return FlDotCirclePainter(
                    radius: 5,
                    color: primaryColor,
                    strokeWidth: 2,
                    strokeColor: Colors.white,
                  );
                },
              ),
              // Add a gradient fill below the line for a modern look
              belowBarData: BarAreaData(
                show: true,
                gradient: LinearGradient(
                  colors: [
                    primaryColor.withOpacity(0.3),
                    primaryColor.withOpacity(0.0),
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // --- HELPER WIDGETS FOR AXIS TITLES (API FIX) ---

  // Builds the widgets for the bottom (X-axis) titles.
  Widget bottomTitleWidgets(double value, TitleMeta meta) {
    final style = GoogleFonts.inter(
      fontWeight: FontWeight.w500,
      color: Colors.grey[400],
      fontSize: 12,
    );
    String text = value.toInt().toString();
    // FIX: The latest fl_chart API prefers returning a simple Text widget.
    // The library now handles the positioning automatically.
    return Padding(
      padding: const EdgeInsets.only(top: 8.0), // Add space from the axis line
      child: Text(text, style: style),
    );
  }

  // Builds the widgets for the left (Y-axis) titles.
  Widget leftTitleWidgets(double value, TitleMeta meta) {
    final style = GoogleFonts.inter(
      fontWeight: FontWeight.w500,
      color: Colors.grey[400],
      fontSize: 12,
    );
    String text = '${value.toInt()}K';
    // FIX: Just return the Text widget directly.
    return Text(text, style: style, textAlign: TextAlign.left);
  }
}
