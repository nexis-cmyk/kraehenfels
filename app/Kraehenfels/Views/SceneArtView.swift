import SwiftUI
import UIKit

struct SceneArtView: View {
    let resourceName: String?
    var height: CGFloat = 190
    var shareLabel: String = "Bild teilen / sichern"

    var body: some View {
        Group {
            if let image = loadImage() {
                Image(uiImage: image)
                    .resizable()
                    .scaledToFill()
            } else {
                ZStack {
                    LinearGradient(colors: [FrostTheme.panelRaised, FrostTheme.ink], startPoint: .topLeading, endPoint: .bottomTrailing)
                    Image(systemName: "mountain.2.fill")
                        .font(.system(size: 48, weight: .light))
                        .foregroundStyle(FrostTheme.cobalt.opacity(0.55))
                }
            }
        }
        .frame(maxWidth: .infinity)
        .frame(height: height)
        .clipped()
        .overlay(alignment: .bottom) {
            LinearGradient(colors: [.clear, FrostTheme.ink.opacity(0.76)], startPoint: .top, endPoint: .bottom)
                .frame(height: 72)
        }
        .overlay(alignment: .topTrailing) {
            if resourceName != nil {
                MaterialShareLink(resourceName: resourceName ?? "", subdirectory: "Art", label: shareLabel)
                    .padding(8)
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(FrostTheme.frost.opacity(0.15), lineWidth: 1))
    }

    private func loadImage() -> UIImage? {
        guard let resourceName,
              let image = BundleMaterialAsset.image(for: resourceName, subdirectory: "Art") else { return nil }
        return image
    }
}
