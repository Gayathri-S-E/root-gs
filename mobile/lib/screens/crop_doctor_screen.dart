import 'package:flutter/material';
import 'package:image_picker/image_picker.dart';

class CropDoctorScreen extends StatefulWidget {
  const CropDoctorScreen({super.key});

  @override
  State<CropDoctorScreen> createState() => _CropDoctorScreenState();
}

class _CropDoctorScreenState extends State<CropDoctorScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _imageFile;
  bool _isLoading = false;
  String? _result;

  Future<void> _pickImage() async {
    final XFile? selected = await _picker.pickImage(source: ImageSource.camera);
    if (selected != null) {
      setState(() {
        _imageFile = selected;
        _result = null;
      });
    }
  }

  Future<void> _analyzeImage() async {
    if (_imageFile == null) return;
    setState(() {
      _isLoading = true;
    });

    // Mock analysis pipeline for mobile app demo
    await Future.delayed(const Duration(seconds: 2));

    setState(() {
      _isLoading = false;
      _result = 'Rice Blast (Magnaporthe oryzae) detected.\nSeverity: Moderate (35% affected).\n\nOrganic Treatment: Apply Pseudomonas fluorescens.\nChemical Treatment: Tricyclazole 75% WP.';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('🔬 Crop Doctor')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Expanded(
              child: Card(
                color: const Color(0xFFF5F9F4),
                child: _imageFile == null
                    ? const Center(child: Text('Take or select a crop photo to analyze'))
                    : Image.asset(_imageFile!.path, fit: BoxFit.cover, errorBuilder: (c, e, s) {
                        return Center(child: Text('Selected crop photo: ${_imageFile!.name}'));
                      }),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _pickImage,
              icon: const Icon(Icons.camera_alt),
              label: const Text('Capture Crop Leaf'),
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF2E7D32), foregroundColor: Colors.white),
            ),
            const SizedBox(height: 8),
            _isLoading
                ? const Center(child: CircularProgressIndicator())
                : ElevatedButton(
                    onPressed: _imageFile != null ? _analyzeImage : null,
                    child: const Text('Analyze with AI'),
                  ),
            if (_result != null) ...[
              const SizedBox(height: 16),
              Card(
                color: const Color(0xFFE8F5E9),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    _result!,
                    style: const TextStyle(fontWeight: FontWeight.w600, color: Colors.black87),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
