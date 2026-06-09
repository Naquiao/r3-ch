import unittest

from r3_ch.adapters.opportunity_normalizer import (
    ATS_ASHBY,
    ATS_BAMBOOHR,
    ATS_GREENHOUSE,
    ATS_LEVER,
    extract_ashby_location,
    extract_bamboohr_location,
    extract_lever_location,
    normalize_ashby_job,
    normalize_bamboohr_job,
    normalize_greenhouse_job,
    normalize_lever_job,
)


class OpportunityNormalizerTests(unittest.TestCase):
    def test_normalize_greenhouse_job_keeps_shared_shape(self) -> None:
        record = normalize_greenhouse_job(
            slug="acme",
            job={
                "id": 42,
                "title": "Senior AI Engineer",
                "updated_at": "2026-06-08T00:00:00Z",
                "absolute_url": "https://boards.greenhouse.io/acme/jobs/42",
                "location": {"name": "Cordoba, Argentina"},
                "content": "<p>Build ML systems</p>",
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ai engineer"],
            eligibility="ok",
        )

        self.assertEqual(record["ats"], ATS_GREENHOUSE)
        self.assertEqual(record["slug"], "acme")
        self.assertEqual(record["job_id"], 42)
        self.assertEqual(record["eligibility"], "ok")
        self.assertEqual(record["location_raw"], "Cordoba, Argentina")
        self.assertEqual(record["description"], "<p>Build ML systems</p>")

    def test_normalize_greenhouse_job_description_fallback(self) -> None:
        record = normalize_greenhouse_job(
            slug="acme",
            job={
                "id": 42,
                "content": "",
                "descriptionPlain": "Fallback desc",
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ai engineer"],
            eligibility="ok",
        )
        self.assertEqual(record["description"], "Fallback desc")

    def test_normalize_ashby_job_description_fallback(self) -> None:
        record = normalize_ashby_job(
            slug="acme",
            job={
                "id": 42,
                "descriptionPlain": "",
                "descriptionHtml": "",
                "content": "Fallback content",
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ai engineer"],
            eligibility="ok",
        )
        self.assertEqual(record["description"], "Fallback content")

    def test_extract_ashby_location_builds_remote_context(self) -> None:
        location = extract_ashby_location(
            {
                "location": "Brazil",
                "secondaryLocations": [{"location": "Argentina"}],
                "workplaceType": "Remote",
                "isRemote": True,
                "address": {"postalAddress": {"addressCountry": "BR"}},
            }
        )
        self.assertEqual(location, "Brazil, Argentina, Remote, remote, BR")

    def test_normalize_ashby_job_falls_back_to_job_url_for_id(self) -> None:
        record = normalize_ashby_job(
            slug="acme",
            job={
                "title": "Applied ML Engineer",
                "jobUrl": "https://jobs.ashbyhq.com/acme/8f2e6f4f-aaaa-bbbb",
                "location": "Remote - LATAM",
                "publishedAt": "2026-06-08T00:00:00Z",
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ml engineer"],
            eligibility="ok",
        )

        self.assertEqual(record["ats"], ATS_ASHBY)
        self.assertEqual(record["job_id"], "8f2e6f4f-aaaa-bbbb")
        self.assertEqual(record["absolute_url"], "https://jobs.ashbyhq.com/acme/8f2e6f4f-aaaa-bbbb")
        self.assertEqual(record["location_raw"], "Remote - LATAM")

    def test_extract_lever_location(self) -> None:
        location = extract_lever_location(
            {
                "categories": {
                    "location": "Remote LATAM",
                    "team": "Engineering",
                    "commitment": "Full-time",
                }
            }
        )
        self.assertEqual(location, "Remote LATAM, Engineering, Full-time")

    def test_normalize_lever_job_fallbacks(self) -> None:
        record = normalize_lever_job(
            slug="acme",
            job={
                "id": "abc123",
                "text": "ML Engineer",
                "hostedUrl": "https://jobs.lever.co/acme/abc123",
                "descriptionPlain": "",
                "description": "",
                "descriptionHtml": "<p>Build models</p>",
                "categories": {"location": "Remote LATAM"},
                "createdAt": 1_717_861_234_000,
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ml engineer"],
            eligibility="ok",
        )
        self.assertEqual(record["ats"], ATS_LEVER)
        self.assertEqual(record["job_id"], "abc123")
        self.assertEqual(record["absolute_url"], "https://jobs.lever.co/acme/abc123")
        self.assertEqual(record["description"], "<p>Build models</p>")

    def test_extract_bamboohr_location(self) -> None:
        location = extract_bamboohr_location(
            {
                "categories": {
                    "location": "Remote LATAM",
                    "department": "Engineering",
                },
                "employmentType": "Full-time",
            }
        )
        self.assertEqual(location, "Full-time, Remote LATAM, Engineering")

    def test_normalize_bamboohr_job(self) -> None:
        record = normalize_bamboohr_job(
            slug="acme",
            job={
                "id": "bh-123",
                "text": "Applied AI Engineer",
                "url": "https://acme.bamboohr.com/careers/123",
                "description": "",
                "descriptionHtml": "<p>GenAI platform</p>",
                "categories": {"location": "Remote LATAM"},
                "createdAt": "2026-06-08T00:00:00Z",
            },
            target_location="Cordoba, Argentina",
            matched_keywords=["ai engineer"],
            eligibility="ok",
        )
        self.assertEqual(record["ats"], ATS_BAMBOOHR)
        self.assertEqual(record["job_id"], "bh-123")
        self.assertEqual(record["absolute_url"], "https://acme.bamboohr.com/careers/123")
        self.assertEqual(record["location_raw"], "Remote LATAM")
        self.assertEqual(record["description"], "<p>GenAI platform</p>")


if __name__ == "__main__":
    unittest.main()
