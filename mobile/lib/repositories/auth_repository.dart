import 'package:dio/dio.dart';
import '../api/api_client.dart';

class AuthRepository {
  final ApiClient apiClient;

  AuthRepository(this.apiClient);

  Future<Map<String, dynamic>?> login(String email, String password) async {
    try {
      final response = await apiClient.dio.post('/auth/login', data: {
        'email': email,
        'password': password,
      });
      if (response.statusCode == 200) {
        final data = response.data['data'];
        await apiClient.secureStorage.write(key: 'access_token', value: data['access_token']);
        await apiClient.secureStorage.write(key: 'refresh_token', value: data['refresh_token']);
        return data['user'];
      }
    } catch (e) {
      rethrow;
    }
    return null;
  }

  Future<void> logout() async {
    await apiClient.secureStorage.delete(key: 'access_token');
    await apiClient.secureStorage.delete(key: 'refresh_token');
  }
}
