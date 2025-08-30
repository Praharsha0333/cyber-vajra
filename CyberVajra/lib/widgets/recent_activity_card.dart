import 'package:flutter/material.dart';
import './glassmorphic_card.dart';

/// A card that displays a list of recent scans with a simple red/green status indicator.
class RecentActivityCard extends StatelessWidget {
  final List<String> recentActivity;

  const RecentActivityCard({super.key, required this.recentActivity});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return GlassmorphicCard(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text("Recent Activity",
                style: theme.textTheme.titleLarge
                    ?.copyWith(fontWeight: FontWeight.bold)),
            Divider(color: Colors.grey[700], height: 24),
            if (recentActivity.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24.0),
                  child: Text("No scans performed yet.",
                      style: TextStyle(color: Colors.grey[400])),
                ),
              )
            else
            // Build a list of the 5 most recent scans
              ...recentActivity
                  .take(5)
                  .map((log) => _buildLogItem(theme, log))
                  .toList(),
          ],
        ),
      ),
    );
  }

  /// Builds a single row in the activity log.
  Widget _buildLogItem(ThemeData theme, String log) {
    // Determine the color based on keywords in the log string.
    final bool isSuspicious =
        log.toLowerCase().contains('risk') || log.toLowerCase().contains('threat');
    final Color indicatorColor =
    isSuspicious ? const Color(0xFFFF4747) : theme.primaryColor;
    final IconData indicatorIcon =
    isSuspicious ? Icons.warning_amber_rounded : Icons.check_circle_outline;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        children: [
          Icon(indicatorIcon, color: indicatorColor, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              log,
              style: TextStyle(color: Colors.grey[300]),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }
}

