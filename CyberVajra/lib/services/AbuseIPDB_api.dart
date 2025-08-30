import 'dart:convert';
import 'package:http/http.dart' as http;

/// Represents a malicious IP record from AbuseIPDB
class AbuseIpRecord {
  final String ipAddress;
  final String countryCode;
  final int abuseConfidenceScore; // A score from 0-100
  final DateTime lastReportedAt;

  AbuseIpRecord({
    required this.ipAddress,
    required this.countryCode,
    required this.abuseConfidenceScore,
    required this.lastReportedAt,
  });
}

// Renamed the class to be more generic
class ThreatDataApi {
  // Base URL for the AbuseIPDB API version 2
  static const _baseUrl = "https://api.abuseipdb.com/api/v2";

  // Your AbuseIPDB API key
  final String apiKey;

  ThreatDataApi(this.apiKey);

  /// Fetches a blacklist of malicious IPs from AbuseIPDB.
  Future<List<AbuseIpRecord>> fetchBlacklist() async {
    // The /blacklist endpoint gives a list of the most reported IPs.
    // We can limit it to 100 results for this example.
    final url = Uri.parse("$_baseUrl/blacklist?limit=100");

    final response = await http.get(
      url,
      headers: {
        'Accept': 'application/json',
        'Key': apiKey, // The header for the API key is 'Key'
      },
    );

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body);
      // The list of IPs is under the 'data' key
      final data = json['data'] as List<dynamic>;

      return data.map((ipData) {
        return AbuseIpRecord(
          ipAddress: ipData['ipAddress'] ?? 'N/A',
          countryCode: ipData['countryCode'] ?? '??',
          abuseConfidenceScore: ipData['abuseConfidenceScore'] ?? 0,
          lastReportedAt: DateTime.parse(ipData['lastReportedAt']),
        );
      }).toList();
    } else {
      throw Exception(
        "Failed to fetch blacklist: ${response.statusCode} ${response.body}",
      );
    }
  }
}