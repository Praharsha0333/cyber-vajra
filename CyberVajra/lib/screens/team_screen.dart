import 'dart:ui';
import 'package:flutter/material.dart';

// --- NOTE ---
// For this to work, you should move the 'GlassmorphicCard' widget
// from your dashboard file into its own file (e.g., 'widgets/glassmorphic_card.dart')
// so you can import and use it here.

// Example of what the import would look like:
// import 'widgets/glassmorphic_card.dart';

// --- Placeholder GlassmorphicCard for demonstration ---
// (Replace this with the import once you move the widget)
class GlassmorphicCard extends StatelessWidget {
  final Widget child;
  const GlassmorphicCard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16.0),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 10.0, sigmaY: 10.0),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16.0),
            border: Border.all(
              color: Colors.white.withOpacity(0.2),
              width: 1.5,
            ),
          ),
          child: child,
        ),
      ),
    );
  }
}


class TeamScreen extends StatelessWidget {
  const TeamScreen({super.key});

  final List<Map<String, String>> teamMembers = const [
    {
      "photo": "assets/members/member1.jpeg",
      "memberNo": "Team Leader",
      "name": "Tashee Bisht",
      "role": "Cybersecurity Expert",
      "about": "Writes code that even aliens can't debug."
    },
    {
      "photo": "assets/members/member2.jpeg",
      "memberNo": "Member 1",
      "name": "Himesh Kumar",
      "role": "App Developer",
      "about": "Knows the answer before you Google it"
    },
    {
      "photo": "assets/members/member3.jpeg",
      "memberNo": "Member 2",
      "name": "Gopal Mohan",
      "role": "Backend Developer",
      "about": "Has 99 ideas a minute—only 3 crash the app"
    },
    {
      "photo": "assets/members/member4.jpeg",
      "memberNo": "Member 3",
      "name": "Praharsha Kumar",
      "role": "AI/ML Developer",
      "about": "Breaks stuff just to fix it better."
    },
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      // Use the same background color as the dashboard
      backgroundColor: const Color(0xFF0A0A0A),
      appBar: AppBar(
        // Transparent app bar for a seamless look
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text(
          "Our Team",
          // Use the theme's text style for consistency
          style: theme.textTheme.headlineSmall?.copyWith(
            fontWeight: FontWeight.bold,
            color: theme.primaryColor, // Neon green title
          ),
        ),
        centerTitle: true,
        iconTheme: IconThemeData(color: theme.primaryColor), // Back button color
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: teamMembers.length,
        itemBuilder: (context, index) {
          final member = teamMembers[index];
          // Use the GlassmorphicCard for each team member
          return Padding(
            padding: const EdgeInsets.only(bottom: 20.0),
            child: GlassmorphicCard(
              child: Padding(
                padding: const EdgeInsets.all(18.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        // --- NEON GLOW EFFECT FOR AVATAR ---
                        Container(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(color: theme.primaryColor, width: 2),
                            boxShadow: [
                              BoxShadow(
                                color: theme.primaryColor.withOpacity(0.7),
                                blurRadius: 10,
                                spreadRadius: 1,
                              ),
                            ],
                          ),
                          child: CircleAvatar(
                            radius: 35,
                            backgroundImage: AssetImage(member["photo"]!),
                            backgroundColor: Colors.grey[800],
                          ),
                        ),
                        const SizedBox(width: 18),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                member["memberNo"]!,
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: Colors.grey[400],
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                member["name"]!,
                                style: theme.textTheme.titleLarge?.copyWith(
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                member["role"]!,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  color: theme.primaryColor, // Use neon green for the role
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    Divider(color: Colors.grey[800]),
                    const SizedBox(height: 12),
                    Text(
                      "\"${member["about"]!}\"",
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.4,
                        color: Colors.grey[300],
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
