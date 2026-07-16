from monitor import canonicalize_url, merge_seen_urls, parse_releases


def test_parse_releases_filters_non_release_links_and_inherits_date():
    html = """
    <div class="view-content">
      <div class="views-row">
        <div class="views-field-field-date"><time>2026-07-13</time></div>
        <div class="views-field-title">
          <a href="/about/policy-offices/press-office/press-releases/2026/july/first-release">First release</a>
        </div>
      </div>
      <div class="views-row">
        <div class="views-field-field-date"><div class="field-content"></div></div>
        <div class="views-field-title">
          <a href="/trade-topics/enforcement/section-201-investigations/section-201-lamb-meat">Not a release</a>
        </div>
      </div>
      <div class="views-row">
        <div class="views-field-title">
          <a href="/about-us/policy-offices/press-office/press-releases/2026/july/second-release">Second release</a>
        </div>
      </div>
      <div class="views-row">
        <div class="views-field-title">
          <a href="/about-us/policy-offices/press-office/press-releases/2026/july">July archive</a>
        </div>
      </div>
    </div>
    """

    releases = parse_releases(html)

    assert [release["title"] for release in releases] == [
        "First release",
        "Second release",
    ]
    assert releases[1]["date"] == "2026-07-13"
    assert releases[1]["link"] == (
        "https://ustr.gov/about/policy-offices/press-office/"
        "press-releases/2026/july/second-release"
    )


def test_canonicalize_url_treats_about_us_as_about_alias():
    about_us = "/about-us/policy-offices/press-office/press-releases/2026/july/release"
    about = "https://ustr.gov/about/policy-offices/press-office/press-releases/2026/july/release/"

    assert canonicalize_url(about_us) == canonicalize_url(about)


def test_merge_seen_urls_keeps_more_than_one_hundred_urls():
    existing = [
        f"https://ustr.gov/about/policy-offices/press-office/press-releases/2025/january/release-{i}"
        for i in range(120)
    ]
    current = [
        "/about-us/policy-offices/press-office/press-releases/2026/july/current-release"
    ]

    merged = merge_seen_urls(existing, current)

    assert len(merged) == 121
    assert merged[0].endswith("release-0")
    assert merged[-1] == (
        "https://ustr.gov/about/policy-offices/press-office/"
        "press-releases/2026/july/current-release"
    )
