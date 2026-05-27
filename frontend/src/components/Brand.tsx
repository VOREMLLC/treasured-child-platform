import Link from "next/link";
import Image from "next/image";

interface BrandProps {
  className?: string;
  alt?: string;
  priority?: boolean;
}

export function Brand({
  className = "",
  alt = "Treasured Child School logo",
  priority = false,
}: BrandProps) {
  return (
    <Link href="/" className={`flex items-center gap-3 ${className}`}>
      <span className="bg-white rounded-[14px] shadow-s p-1.5 inline-flex">
        <Image
          src="/logo.png"
          alt={alt}
          width={36}
          height={36}
          className="object-contain"
          priority={priority}
        />
      </span>
      <span className="font-display font-bold text-paper text-[17px] leading-none">
        Treasured Child
        <small className="block font-body font-semibold text-[9.5px] tracking-[0.16em] uppercase text-gold pt-1">
          Nursery · primary · secondary
        </small>
      </span>
    </Link>
  );
}
