# Product artwork

This directory owns the banner and workbench screenshots displayed by the public
README. They explain the product and do not participate in benchmark execution,
input hashes, or expected results. Keep screenshots separate from measured claims.

`wald-banner.svg` is approved, outlined Wald artwork in the fineSample brand
palette. Its text uses Instrument Sans, the workbench's typeface; the SVG loads
no fonts or external resources. Replace it with an approved export when the
wording changes. The rendering utility named in its generated header belongs
to the product's documentation authoring tools, not the benchmark runtime.

`workbench-queue.jpg` and `workbench-facts.jpg` are unedited browser captures
of Wald's full development runtime, taken on 2 October 2026 at 1311 by 850.
They contain only synthetic account and payment histories. The queue shows
real native scorecard answers marked as starting points, with no calibration
or automatic release claimed. The application uses the fineSample wordmark.

When replacing a screenshot, use an isolated development store with synthetic
data. Keep the development-stage label and missing-evidence states visible.
Exclude browser chrome, authentication fragments, credentials, and customer
data. Never alter a displayed score or result for a screenshot. Update the
README caption if the release boundary changes.

These images preview the full product. The public 0.1 offering supports an
offline historical assessment and decision-pack validation, not deployment of
the pictured workbench. The repository's licensing section distinguishes the
benchmark source from Wald's product, binary, and trademarks.
