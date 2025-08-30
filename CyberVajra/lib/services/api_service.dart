import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;

class ApiService {
  // ✅ change this to your machine’s IP (keep it same as Flask run output)
  static const baseUrl = "http://10.91.12.232:5001";
  static const baseUrl2 = "http://10.91.12.148:5001";

  // ---------- URL Scan ----------
  // ---------- URL Scan ----------
  static Future<Map<String, dynamic>> scanUrl(String url) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl2/api/analyze_url"), // <-- FIXED
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"url": url}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        return {
          "error": "Failed with status ${response.statusCode}",
          "body": response.body
        };
      }
    } catch (e) {
      return {"error": e.toString()};
    }
  }


  // ---------- APK Scan ----------
  static Future<Map<String, dynamic>> scanApk(File file) async {
    try {
      var request = http.MultipartRequest(
        "POST",
        Uri.parse("$baseUrl/analyze_apk"),
      );
      request.files.add(
        await http.MultipartFile.fromPath("file", file.path),
      );

      var streamedResponse = await request.send();
      var respStr = await streamedResponse.stream.bytesToString();

      if (streamedResponse.statusCode == 200) {
        return jsonDecode(respStr);
      } else {
        return {
          "error": "Failed with status ${streamedResponse.statusCode}",
          "body": respStr
        };
      }
    } catch (e) {
      return {"error": e.toString()};
    }
  }
}
