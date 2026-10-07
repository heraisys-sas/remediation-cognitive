// Transcription sur l'appareil uniquement ; aucun téléchargement d'assets.
import Foundation
import Speech
import AVFoundation

@main struct Dictee {
    static func emit(_ value: [String: Any]) {
        if let data = try? JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]),
           let text = String(data: data, encoding: .utf8) { print(text) }
    }
    static func main() async {
        guard #available(macOS 26.0, *) else {
            emit(["disponible": false, "raison": "macos_26_requis"]); return
        }
        guard SpeechTranscriber.isAvailable else {
            emit(["disponible": false, "raison": "moteur_indisponible"]); return
        }
        let locales = await SpeechTranscriber.installedLocales
        guard let locale = locales.first(where: { $0.identifier.replacingOccurrences(of: "_", with: "-") == "fr-FR" }) else {
            emit(["disponible": false, "raison": "francais_non_installe"]); return
        }
        if CommandLine.arguments.count == 2 && CommandLine.arguments[1] == "--status" {
            emit(["disponible": true, "fournisseur": "apple_speech_local", "langue": "fr-FR"]); return
        }
        guard CommandLine.arguments.count == 2 else {
            emit(["disponible": false, "raison": "argument_invalide"]); return
        }
        do {
            let transcriber = SpeechTranscriber(locale: locale, transcriptionOptions: [], reportingOptions: [], attributeOptions: [])
            let analyzer = SpeechAnalyzer(modules: [transcriber])
            let collection = Task { () throws -> String in
                var parts: [String] = []
                for try await result in transcriber.results { parts.append(String(result.text.characters)) }
                return parts.joined(separator: " ").trimmingCharacters(in: .whitespacesAndNewlines)
            }
            do {
                let file = try AVAudioFile(forReading: URL(fileURLWithPath: CommandLine.arguments[1]))
                try await analyzer.start(inputAudioFile: file, finishAfterFile: true)
                let text = try await collection.value
                if text.isEmpty {
                    emit(["disponible": false, "raison": "parole_non_detectee"])
                } else {
                    emit(["disponible": true, "texte": text, "fournisseur": "apple_speech_local"])
                }
            } catch {
                collection.cancel()
                await analyzer.cancelAndFinishNow()
                throw error
            }
        } catch {
            emit(["disponible": false, "raison": "transcription_echouee"])
        }
    }
}
