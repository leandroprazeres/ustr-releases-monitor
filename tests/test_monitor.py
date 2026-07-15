from monitor import parse_releases


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
