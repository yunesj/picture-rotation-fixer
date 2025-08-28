class PictureRotationFixer < Formula
  desc "Effortlessly auto-rotate scanned photos to the correct orientation"
  homepage "https://github.com/JustinGuese/picture-rotation-fixer"
  version "0.0.1"
  

  url "https://github.com/JustinGuese/picture-rotation-fixer/releases/download/v#{version}/picture-rotation-fixer"
  sha256 "cf3ba56171899864ad1c5c47d15786482a4e2081cc820670dec3cba9913708a8"

  def install
    bin.install "picture-rotation-fixer"
  end

  test do
    system "#{bin}/picture-rotation-fixer", "--help"
  end
end
