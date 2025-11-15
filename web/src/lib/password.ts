import argon2 from 'argon2';

export type HashOptions = {
  memoryCost?: number;
  timeCost?: number;
  parallelism?: number;
};

export type HashResult = {
  hash: string;
  verify: (password: string) => Promise<boolean>;
};

export class PasswordHasher {
  /**
   * Hash a password using Argon2id
   */
  static async hashPassword(password: string, options?: HashOptions): Promise<string> {
    const hashOptions: any = {
      type: argon2.argon2id,
      memoryCost: options?.memoryCost || 65536, // 64 MB
      timeCost: options?.timeCost || 3,         // 3 iterations
      parallelism: options?.parallelism || 4,   // 4 threads
    };

    try {
      const hash = await argon2.hash(password, hashOptions);
      return hash;
    } catch (error) {
      console.error('Error hashing password:', error);
      throw new Error('Failed to hash password');
    }
  }

  /**
   * Verify a password against its hash
   */
  static async verifyPassword(hash: string, password: string): Promise<boolean> {
    try {
      return await argon2.verify(hash, password);
    } catch (error) {
      console.error('Error verifying password:', error);
      return false;
    }
  }

  /**
   * Check if a hash string is a valid Argon2 hash
   */
  static isValidHash(hash: string): boolean {
    return hash.startsWith('$argon2id$') || 
           hash.startsWith('$argon2i$') || 
           hash.startsWith('$argon2d$');
  }
}

export const hashPassword = (password: string, options?: HashOptions) => 
  PasswordHasher.hashPassword(password, options);

export const verifyPassword = (hash: string, password: string) => 
  PasswordHasher.verifyPassword(hash, password);

export const isValidHash = (hash: string) => 
  PasswordHasher.isValidHash(hash);