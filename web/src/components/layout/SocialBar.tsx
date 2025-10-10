import { FaFacebookF, FaLinkedinIn, FaInstagram, FaGithub } from "react-icons/fa";

export default function SocialBar() {
  const items = [
    { href: "https://www.facebook.com/?locale=es_LA", Icon: FaFacebookF, label: "Facebook" },
    { href: "https://cl.linkedin.com", Icon: FaLinkedinIn, label: "LinkedIn" },
    { href: "https://www.instagram.com", Icon: FaInstagram, label: "Instagram" },
    { href: "https://github.com/SiegAxel/EncryptU", Icon: FaGithub, label: "GitHub" },
  ];
  return (
    <div className="flex items-center gap-3">
      {items.map(({ href, Icon, label }) => (
        <a
          key={label}
          href={href}
          aria-label={label}
          className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-300 hover:bg-slate-50"
        >
          <Icon />
        </a>
      ))}
    </div>
  );
}
