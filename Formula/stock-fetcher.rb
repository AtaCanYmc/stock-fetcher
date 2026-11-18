class StockFetcher < Formula
  include Language::Python::Virtualenv

  desc "CLI utility for searching and downloading copyright-free stock photos"
  homepage "https://github.com/AtaCanYmc/stock-fetcher"
  url "https://github.com/AtaCanYmc/stock-fetcher/archive/refs/tags/v0.2.0.tar.gz"
  sha256 "c7d2cf54b7207b7bbac23bd695925a4a8f49db9a5d9b9c90e2a3f8416ebe0f3a"
  license "Apache-2.0"
  head "https://github.com/AtaCanYmc/stock-fetcher.git", branch: "main"

  depends_on "python@3.12"

  def install
    virtualenv_create(libexec, "python3.12")
    system libexec/"bin/pip", "install", "-v", ".[cli]"
    bin.install_symlink libexec/"bin/stock-fetcher"
  end

  test do
    assert_match "stock-fetcher", shell_output("#{bin}/stock-fetcher version")
  end
end
