/**
 * Programme catalogue: the single source of truth for the public
 * programme pages, the home page cards and the pay page choices.
 *
 * Prices here are for DISPLAY only. The amount actually charged is
 * decided server-side (backend/app/services/fees.py); keep the two in
 * step when the proprietor confirms the fee schedule.
 */

import type { IconName } from "@/components/Icon";
import type { PaymentPurpose } from "@/lib/api";

export type ProgrammeKind = "school" | "online";

/** School fees per term, in naira (mirrors FEES_KOBO on the server). */
export const SCHOOL_FEES_NAIRA = 125_000;

export interface Programme {
  slug: string;
  title: string;
  kind: ProgrammeKind;
  isPaid: boolean;
  icon: IconName;

  summary: string;
  description: string[];
  whatsIncluded: string[];

  ageRange: string;
  level: string;

  /** Display price in naira and what it covers. */
  priceNaira: number;
  pricePer: string;
}

export const PROGRAMMES: Programme[] = [
  {
    slug: "nursery",
    title: "Nursery",
    kind: "school",
    isPaid: false,
    icon: "heart",
    summary:
      "Early learning that builds curiosity, language and confidence in a warm, caring class.",
    description: [
      "Our youngest learners learn through structured play, early reading, early numbers and the friendly habits that make later school life easier.",
      "Classes stay small so every child is known by name. Songs, stories and daily routines shape the week.",
    ],
    whatsIncluded: [
      "Phonics-led early reading and writing",
      "Counting and numbers through play",
      "Music, movement and creative arts",
      "Daily story time and outdoor play",
      "Updates for parents every term",
    ],
    ageRange: "3 to 5 years",
    level: "Nursery",
    priceNaira: SCHOOL_FEES_NAIRA,
    pricePer: "per term",
  },
  {
    slug: "primary",
    title: "Primary",
    kind: "school",
    isPaid: false,
    icon: "book",
    summary:
      "Strong reading, writing and maths, with first steps into science and computers.",
    description: [
      "Primary 1 to 6 builds a strong foundation: confident reading, secure maths, clear writing and a growing curiosity about the world.",
      "Pupils prepare for Common Entrance in their final year. We pair classroom discipline with project work, music and sport.",
    ],
    whatsIncluded: [
      "English, maths and basic science",
      "Social studies, agriculture and creative arts",
      "Introduction to computers",
      "Common Entrance preparation in Primary 6",
      "Report card every term",
    ],
    ageRange: "6 to 11 years",
    level: "Primary",
    priceNaira: SCHOOL_FEES_NAIRA,
    pricePer: "per term",
  },
  {
    slug: "junior-secondary",
    title: "Junior secondary (JSS 1 to 3)",
    kind: "school",
    isPaid: false,
    icon: "school",
    summary:
      "The core years that prepare learners for BECE and senior secondary.",
    description: [
      "JSS 1 to JSS 3 covers the full Nigerian national curriculum: English, maths, basic science and technology, social studies, agriculture, creative arts and computer studies.",
      "Classes stay small and parents get a report every term. BECE practice is built into JSS 3, with mock exams and personal feedback.",
    ],
    whatsIncluded: [
      "Full national JSS curriculum",
      "Maths, English, basic science, social studies",
      "Safe, supervised computer studies",
      "BECE mock exams in JSS 3",
      "Small classes and termly reports",
    ],
    ageRange: "10 to 13 years",
    level: "Junior secondary",
    priceNaira: SCHOOL_FEES_NAIRA,
    pricePer: "per term",
  },
  {
    slug: "senior-secondary",
    title: "Senior secondary (SS 1 to 3)",
    kind: "school",
    isPaid: false,
    icon: "star",
    summary: "Science, commercial and arts classes leading to WAEC and JAMB.",
    description: [
      "SS 1 to SS 3 learners choose science, commercial or arts subjects and sit WAEC at the end of SS 3.",
      "Regular mock exams and personal study plans carry learners through to university or further training.",
    ],
    whatsIncluded: [
      "Science, commercial and arts classes",
      "WAEC and JAMB preparation",
      "Regular mock exams",
      "University and career guidance",
      "Small classes and termly reports",
    ],
    ageRange: "13 to 17 years",
    level: "Senior secondary",
    priceNaira: SCHOOL_FEES_NAIRA,
    pricePer: "per term",
  },
  {
    slug: "bece-prep",
    title: "Common Entrance and BECE prep",
    kind: "online",
    isPaid: true,
    icon: "book",
    summary:
      "Short online lessons in maths, English and reasoning, with a friendly helper for stuck moments.",
    description: [
      "Online exam practice for Common Entrance and BECE. Weekly mock tests, a safe AI helper inside every lesson, and progress you can see as a parent.",
      "Works anywhere in Nigeria on a phone. Lessons are short and focused, and the helper only talks about the lesson your child is on.",
    ],
    whatsIncluded: [
      "Maths, English, verbal and number reasoning",
      "Weekly mock tests with clear feedback",
      "A safe AI helper inside every lesson",
      "Progress reports parents can see",
      "Join term by term",
    ],
    ageRange: "9 to 13 years",
    level: "Online",
    priceNaira: 20_000,
    pricePer: "per term",
  },
  {
    slug: "ai-data",
    title: "AI and data for young people",
    kind: "online",
    isPaid: true,
    icon: "sparkle",
    summary:
      "A friendly first course in AI and data for ages 12 and up. Learn by building small projects.",
    description: [
      "A friendly introduction to AI and data for ages 12 and above. Learners build small projects step by step: spreadsheets, then charts, then simple AI notebooks.",
      "Small groups. A parent or guardian agrees before a learner account is switched on.",
    ],
    whatsIncluded: [
      "Data basics: spreadsheets, charts and simple statistics",
      "First steps with Python notebooks",
      "Three hands-on projects to keep",
      "A safe AI helper inside every lesson",
      "Parent consent before the account starts",
    ],
    ageRange: "12 years and up",
    level: "Online",
    priceNaira: 35_000,
    pricePer: "per course",
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

export function formatNaira(naira: number): string {
  return `₦${naira.toLocaleString("en-NG")}`;
}

// ── Pay page choices ────────────────────────────────────────

export interface PayChoice {
  /** Stable key used in the URL (?for=...) and as the radio value. */
  key: string;
  title: string;
  description: string;
  priceNaira: number;
  icon: IconName;
  purpose: PaymentPurpose;
  target?: string;
}

export const PAY_CHOICES: PayChoice[] = [
  {
    key: "fees",
    title: "School fees",
    description: "One term, any class",
    priceNaira: SCHOOL_FEES_NAIRA,
    icon: "school",
    purpose: "fees",
  },
  ...getOnlineProgrammes().map<PayChoice>((p) => ({
    key: p.slug,
    title: p.title,
    description: `Online, ${p.pricePer}`,
    priceNaira: p.priceNaira,
    icon: p.icon,
    purpose: "programme",
    target: p.slug,
  })),
];
