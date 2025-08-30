import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../widgets/glassmorphic_card.dart'; // Import your custom card

class LearnScreen extends StatelessWidget {
  const LearnScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // A list of the learning resources to display
    final List<Map<String, String>> learningResources = [
      {
        "imagePath": "assets/learn/manual.png",
        "title": "Citizen Manual",
        "description": "Official guide for citizens on using the cybercrime portal.",
        "url": "https://cybercrime.gov.in/UploadMedia/MHA-CitizenManualReportOtherCyberCrime-v10.pdf",
      },
      {
        "imagePath": "assets/learn/safety.png",
        "title": "Cyber Safety Tips",
        "description": "Best practices to protect yourself from online threats.",
        "url": "https://cybercrime.gov.in/UploadMedia/index.html",
      },
      {
        "imagePath": "assets/learn/awareness.png",
        "title": "Cyber Awareness",
        "description": "Learn about common threats and how to act responsibly.",
        "url": "https://cybercrime.gov.in/pdf/Final_English_Manual_Basic.pdf",
      },
      {
        "imagePath": "assets/learn/certin.png",
        "title": "CERT-In Directions",
        "description": "Official cybersecurity guidelines issued by CERT-In.",
        "url": "https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf",
      },
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "📚 Learning Corner",
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
        backgroundColor: Colors.transparent, // Make it blend with the neon theme
        elevation: 0,
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(20.0),
        itemCount: learningResources.length,
        itemBuilder: (context, index) {
          final resource = learningResources[index];
          return Padding(
            padding: const EdgeInsets.only(bottom: 20.0),
            child: LearnCard(
              imagePath: resource['imagePath']!,
              title: resource['title']!,
              description: resource['description']!,
              url: resource['url']!,
            ),
          );
        },
      ),
    );
  }
}

/// A redesigned card widget for displaying a single learning resource.
class LearnCard extends StatelessWidget {
  final String imagePath;
  final String title;
  final String description;
  final String url;

  const LearnCard({
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

    return GestureDetector(
      onTap: () => _launchURL(context, url),
      child: GlassmorphicCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // --- FIX: The Stack now correctly wraps the image and the icon ---
            Stack(
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
                    // --- UPDATE: Changed fit from cover to contain ---
                    // This ensures the entire image is visible, effectively "zooming out".
                    fit: BoxFit.contain,
                  ),
                ),
                // --- EXTERNAL LINK ICON ---
                // Positioned correctly in the top-right corner of the image
                Positioned(
                  top: 12,
                  right: 12,
                  child: Icon(
                    Icons.open_in_new,
                    color: Colors.white.withOpacity(0.8),
                    size: 20,
                  ),
                ),
              ],
            ),

            // --- GLOWING DIVIDER ---
            Container(
              height: 2,
              decoration: BoxDecoration(
                boxShadow: [
                  BoxShadow(
                    color: theme.primaryColor.withOpacity(0.5),
                    blurRadius: 4,
                  ),
                ],
                color: theme.primaryColor,
              ),
            ),

            // --- TEXT CONTENT SECTION ---
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
                        ?.copyWith(color: Colors.grey[300]),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

