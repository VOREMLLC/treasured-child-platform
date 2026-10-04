import Link from "next/link";
import Image from "next/image";

interface BrandProps {
  className?: string;
  priority?: boolean;
  href?: string;
}

export function Brand({ className = "", priority = false, href = "/" }: BrandProps) {
  return (
    <Link
      href={href}
      className={`flex min-h-12 items-center gap-3 rounded-control ${className}`}
    >
      {/* The logo PNG has its own light background, so it sits on a
          light chip in both themes. */}
      <span className="inline-flex rounded-control bg-white p-1 shadow-s">
        <Image
          src="/logo.png"
          alt=""
          width={40}
          height={33}
          className="h-[33px] w-10 object-contain"
          priority={priority}
        />
      </span>
      <span className="font-display text-title font-bold leading-none text-ink">
        Treasured Child
        <span className="block pt-1 font-body text-caption font-semibold text-muted">
          School, Orerokpe
        </span>
      </span>
    </Link>
  );
}
