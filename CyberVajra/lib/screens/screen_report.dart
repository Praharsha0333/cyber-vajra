import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../widgets/glassmorphic_card.dart'; // Import your custom card

class ReportScreen extends StatelessWidget {
  const ReportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    // A list of the reporting categories to display
    final List<Map<String, dynamic>> reportCategories = [
      {
        "imagePath": "assets/reports/financial_fraud.jpg",
        "title": "Financial Fraud",
        "description": "Report online financial scams, phishing, or unauthorized transactions.",
        "url": "https://cybercrime.gov.in/Webform/Accept.aspx",
      },
      {
        "imagePath": "assets/reports/women_children.jpeg",
        "title": "Women/Child Crime",
        "description": "Report online harassment, cyberstalking, or exploitation.",
        "url": "https://cybercrime.gov.in/Webform/Accept.aspx",
      },
      {
        "imagePath": "assets/reports/other_cyber.jpeg",
        "title": "Other Cyber Crime",
        "description": "Report other cybercrimes like hacking, data theft, or online threats.",
        "url": "https://cybercrime.gov.in/Webform/Accept.aspx",
      },
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "📢 Report Cyber Crimes",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent, // Make it blend with the neon theme
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20.0),
        children: [
          // --- NEW: Disclaimer Card ---
          GlassmorphicCard(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Icon(Icons.info_outline, color: Colors.yellow[600]),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      "You will be redirected to the official National Cyber Crime Reporting Portal (cybercrime.gov.in).",
                      style: theme.textTheme.bodyMedium
                          ?.copyWith(color: Colors.grey[300]),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          // --- Use ListView.builder for a more efficient list ---
          ListView.builder(
            itemCount: reportCategories.length,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemBuilder: (context, index) {
              final category = reportCategories[index];
              return Padding(
                padding: const EdgeInsets.only(bottom: 20.0),
                child: ReportCard(
                  imagePath: category['imagePath']!,
                  title: category['title']!,
                  description: category['description']!,
                  url: category['url']!,
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}

/// A redesigned card widget for a single reporting category.
class ReportCard extends StatelessWidget {
  final String imagePath;
  final String title;
  final String description;
  final String url;

  const ReportCard({
    super.key,
    required this.imagePath,
    required this.title,
    required this.description,
    required this.url,
  });

  Future<void> _launchURL(BuildContext context, String url) async {
    final Uri uri = Uri.parse(url);
    if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not launch $url')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final redColor = Colors.red[600]!;

    return GlassmorphicCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // --- IMAGE SECTION ---
          ClipRRect(
            borderRadius: const BorderRadius.only(
              topLeft: Radius.circular(16.0),
              topRight: Radius.circular(16.0),
            ),
            child: Image.asset(
              imagePath,
              height: 120,
              width: double.infinity,
              fit: BoxFit.cover,
            ),
          ),

          // --- GLOWING RED DIVIDER ---
          Container(
            height: 2,
            decoration: BoxDecoration(
              boxShadow: [
                BoxShadow(color: redColor.withOpacity(0.5), blurRadius: 4),
              ],
              color: redColor,
            ),
          ),

          // --- TEXT AND BUTTON SECTION ---
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: theme.textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  description,
                  style: theme.textTheme.bodyMedium
                      ?.copyWith(color: Colors.grey[400]),
                ),
                const SizedBox(height: 16),
                // --- STYLED BUTTON (RED) ---
                ElevatedButton.icon(
                  onPressed: () => _launchURL(context, url),
                  icon: const Icon(Icons.gavel, size: 18),
                  label: const Text("Register Complaint"),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: redColor,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

