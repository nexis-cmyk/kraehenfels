import SwiftUI
import UIKit

struct SceneArtView: View {
    let resourceName: String?
    var height: CGFloat = 190

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
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: 20, style: .continuous).stroke(FrostTheme.frost.opacity(0.15), lineWidth: 1))
        .accessibilityHidden(true)
    }

    private func loadImage() -> UIImage? {
        guard let resourceName,
              let url = Bundle.main.url(forResource: resourceName.replacingOccurrences(of: ".png", with: ""), withExtension: "png", subdirectory: "Art"),
              let data = try? Data(contentsOf: url) else { return nil }
        return UIImage(data: data)
    }
}
