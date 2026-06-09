import unittest

from r3_ch.ats.bamboohr_client import (
    _extract_jobs_from_html,
    _extract_jobs_from_json_payload,
)


class BambooHrClientParsingTests(unittest.TestCase):
    def test_extract_jobs_from_json_payload_list(self) -> None:
        jobs = _extract_jobs_from_json_payload(
            [
                {"id": "1", "title": "ML Engineer"},
                {"id": "2", "title": "Backend Engineer"},
            ]
        )
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "ML Engineer")

    def test_extract_jobs_from_json_payload_nested_data(self) -> None:
        jobs = _extract_jobs_from_json_payload(
            {"data": [{"id": "3", "title": "Applied AI Engineer"}]}
        )
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["id"], "3")

    def test_extract_jobs_from_html_json_ld(self) -> None:
        html = """
        <html><body>
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "JobPosting",
          "title": "AI Engineer",
          "description": "Build AI systems",
          "url": "https://acme.bamboohr.com/careers/42",
          "datePosted": "2026-06-08",
          "jobLocation": {
            "@type": "Place",
            "address": {
              "@type": "PostalAddress",
              "addressLocality": "Cordoba",
              "addressCountry": "AR"
            }
          }
        }
        </script>
        </body></html>
        """
        jobs = _extract_jobs_from_html(html)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "AI Engineer")
        self.assertEqual(jobs[0]["location"], "Cordoba, AR")


if __name__ == "__main__":
    unittest.main()
