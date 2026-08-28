import SwiftUI
import UIKit

enum BundleMaterialAsset {
    static func url(for resourceName: String, subdirectory: String) -> URL? {
        let file = resourceName as NSString
        let name = file.deletingPathExtension
        let fileExtension = file.pathExtension
        guard !name.isEmpty else { return nil }
        return Bundle.main.url(
            forResource: name,
            withExtension: fileExtension.isEmpty ? nil : fileExtension,
            subdirectory: subdirectory
        )
    }

    static func image(for resourceName: String, subdirectory: String) -> UIImage? {
        guard let url = url(for: resourceName, subdirectory: subdirectory),
              let data = try? Data(contentsOf: url) else { return nil }
        return UIImage(data: data)
    }
}

struct MaterialImagePreview: View {
    let resourceName: String
    let subdirectory: String
    var maxHeight: CGFloat? = nil
    var accessibilityLabel: String = "Materialvorschau"

    var body: some View {
        Group {
            if let image = BundleMaterialAsset.image(for: resourceName, subdirectory: subdirectory) {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
            } else {
                ZStack {
                    FrostTheme.panelRaised
                    Label("Vorschau nicht verfügbar", systemImage: "photo.slash")
                        .font(.caption.weight(.semibold))
                        .foregroundStyle(FrostTheme.quiet)
                        .padding()
                }
                .frame(minHeight: 120)
            }
        }
        .frame(maxWidth: .infinity)
        .frame(maxHeight: maxHeight)
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay {
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(FrostTheme.frost.opacity(0.16), lineWidth: 1)
        }
        .accessibilityLabel(accessibilityLabel)
    }
}

struct MaterialShareLink: View {
    let resourceName: String
    let subdirectory: String
    var label: String = "Bild teilen / sichern"

    var body: some View {
        if let url = BundleMaterialAsset.url(for: resourceName, subdirectory: subdirectory) {
            ShareLink(item: url) {
                Label(label, systemImage: "square.and.arrow.up")
                    .font(.caption.weight(.bold))
                    .foregroundStyle(FrostTheme.ink)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 9)
                    .background(FrostTheme.cobalt, in: Capsule())
            }
            .accessibilityLabel(label)
            .accessibilityHint("Öffnet die iOS-Teilen-Funktion für WhatsApp oder zum Sichern.")
        }
    }
}
