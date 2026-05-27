/**
 * Programme catalogue — the single source of truth for the public
 * /programmes pages. Both the catalogue (`/programmes`) and the detail
 * route (`/programmes/[slug]`) read from this list.
 *
 * Later (slice S14) this is replaced by a database read; the shape of
 * `Programme` below stays close to the eventual `Course` schema in
 * BUILD_SPEC §4 so the swap is mechanical.
 */

export type ProgrammeKind = "school" | "online";
export type PillVariant = "blue" | "gold";

export interface Programme {
  slug: string;
  title: string;

  // Card / detail visuals
  bandLabel: string;
  bandGradient: string;
  bandTextColor?: string;
  pill: string;
  pillVariant?: PillVariant;

  // Classification
  kind: ProgrammeKind;
  isPaid: boolean;

  // Copy
  summary: string;
  description: string[];
  whatsIncluded: string[];

  // Meta
  ageRange: string;
  level: string;

  // Paid programmes carry a price note until BUILD_SPEC §14 item 1
  // (the fee table) is supplied by the proprietor.
  priceNote?: string;
}

export const PROGRAMMES: Programme[] = [
  {
    slug: "nursery",
    title: "Nursery",
    bandLabel: "Nursery",
    bandGradient: "linear-gradient(135deg, var(--blue-deep), var(--navy))",
    pill: "School · on campus",
    kind: "school",
    isPaid: false,
    summary:
      "Early learning that builds curiosity, language and confidence — in a warm, structured environment.",
    description: [
      "Our Nursery programme welcomes our youngest learners with structured play, early literacy, early numeracy, and the social habits that make later school life easier.",
      "Class sizes stay small so every child is known by name. Daily routines, songs and stories anchor the week.",
    ],
    whatsIncluded: [
      "Phonics-led early reading and writing",
      "Foundational numeracy through play",
      "Music, movement and creative arts",
      "Daily story time and outdoor play",
      "Termly parent-teacher updates",
    ],
    ageRange: "3–5 years",
    level: "Nursery",
  },
  {
    slug: "primary",
    title: "Primary",
    bandLabel: "Primary",
    bandGradient: "linear-gradient(135deg, var(--blue-deep), var(--navy))",
    pill: "School · on campus",
    kind: "school",
    isPaid: false,
    summary:
      "Strong reading, writing and arithmetic foundations, with first steps into science and digital literacy.",
    description: [
      "Primary years (1 through 6) build a strong academic foundation — fluent reading, secure mathematics, clear written work, and a growing sense of curiosity about the world.",
      "Pupils sit Common Entrance preparation in their final year. We pair classroom discipline with project work, music, and physical education.",
    ],
    whatsIncluded: [
      "English, mathematics, basic science",
      "Social studies, agricultural science, creative arts",
      "Introduction to digital literacy",
      "Common Entrance preparation in P6",
      "Termly parent reports",
    ],
    ageRange: "6–11 years",
    level: "Primary",
  },
  {
    slug: "junior-secondary",
    title: "Junior secondary (JSS 1–3)",
    bandLabel: "Junior secondary",
    bandGradient: "linear-gradient(135deg, var(--blue-deep), var(--navy))",
    pill: "School · on campus",
    kind: "school",
    isPaid: false,
    summary:
      "The core academic years that prepare learners for BECE and senior secondary.",
    description: [
      "Junior Secondary (JSS 1 to JSS 3) covers the core Nigerian national curriculum. Learners take English, mathematics, basic science and technology, social studies, agricultural science, creative arts and digital literacy.",
      "Class sizes stay small. Termly reports go to parents. BECE preparation is built into JSS 3, with mock examinations and individual feedback.",
    ],
    whatsIncluded: [
      "Full national JSS curriculum",
      "Mathematics, English, basic science, social studies",
      "Digital literacy with safety guardrails",
      "BECE mock examinations in JSS 3",
      "Small class sizes and termly reports",
    ],
    ageRange: "10–13 years",
    level: "Junior secondary",
  },
  {
    slug: "senior-secondary",
    title: "Senior secondary (SS 1–3)",
    bandLabel: "Senior secondary",
    bandGradient: "linear-gradient(135deg, var(--blue-deep), var(--navy))",
    pill: "School · on campus",
    kind: "school",
    isPaid: false,
    summary:
      "Sciences, commercial and arts streams leading to WAEC and JAMB.",
    description: [
      "Senior Secondary covers SS 1 through SS 3. Learners specialise across science, commercial and arts streams and sit WAEC at the end of SS 3.",
      "Strong preparation, regular mock examinations and personal study planning carry learners through to university or further training.",
    ],
    whatsIncluded: [
      "Science, commercial and arts streams",
      "WAEC and JAMB preparation",
      "Regular mock examinations",
      "University and career guidance",
      "Small class sizes and termly reports",
    ],
    ageRange: "13–17 years",
    level: "Senior secondary",
  },
  {
    slug: "bece-prep",
    title: "Common entrance & BECE prep",
    bandLabel: "BECE prep",
    bandGradient: "linear-gradient(135deg, var(--blue), var(--blue-bright))",
    pill: "Online · paid",
    kind: "online",
    isPaid: true,
    priceNote:
      "Term-by-term pricing. Final fee to be confirmed by the proprietor.",
    summary:
      "Targeted online practice in maths, English and verbal reasoning with the AI tutor on hand.",
    description: [
      "Online exam-preparation programme for Common Entrance and BECE. Weekly mock tests, AI tutor on hand for stuck moments, parent-visible progress reports.",
      "Suitable for learners anywhere in Nigeria. Lessons are short, focused and child-safe by design — the AI tutor follows the VOREM pedagogy and never strays from the lesson it is bound to.",
    ],
    whatsIncluded: [
      "Maths, English, verbal reasoning, quantitative reasoning",
      "Weekly mock tests with detailed feedback",
      "AI tutor inside every lesson (child-safety guardrails)",
      "Parent-visible progress reports",
      "Term-by-term enrolment",
    ],
    ageRange: "9–13 years",
    level: "Online",
  },
  {
    slug: "ai-data",
    title: "AI & data analytics",
    bandLabel: "AI & data",
    bandGradient: "linear-gradient(135deg, var(--gold-deep), var(--gold))",
    bandTextColor: "#2a1f00",
    pill: "Online · flagship",
    pillVariant: "gold",
    kind: "online",
    isPaid: true,
    priceNote:
      "Cohort-based pricing. Final fee to be confirmed by the proprietor.",
    summary:
      "An accessible introduction to AI and data — designed for ages 12+. Project-based, with safety guardrails throughout.",
    description: [
      "An accessible introduction to AI and data analytics — designed for ages 12 and above. Project-based, with safety guardrails throughout. Learners build small portfolio projects (spreadsheets → charts → simple ML notebooks).",
      "Limited cohort sizes. Parental consent is required before a learner account is activated.",
    ],
    whatsIncluded: [
      "Foundations of data: spreadsheets, charts, summary statistics",
      "Introduction to Python notebooks",
      "Three hands-on projects (portfolio-ready)",
      "AI tutor inside every lesson, with safety guardrails",
      "Parental consent gate before account activation",
    ],
    ageRange: "12+ years",
    level: "Online",
  },
];

export function getProgramme(slug: string): Programme | undefined {
  return PROGRAMMES.find((p) => p.slug === slug);
}

export function getSchoolProgrammes(): Programme[] {
  return PROGRAMMES.filter((p) => p.kind === "school");
}

export function getOnlineProgrammes(): Programme[] {
  return PROGRAMMES.filter((p) => p.kind === "online");
}
