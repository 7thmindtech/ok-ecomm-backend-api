import Category from '../models/Category';

/**
 * Converts a string to a URL-friendly slug
 * @param text The text to convert to a slug
 * @returns A URL-friendly slug
 */
export function slugify(text: string): string {
  return text
    .toString()
    .normalize('NFKD') // Normalize to decomposed form for handling accents
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(/[^\w\-]+/g, '') // Remove all non-word chars
    .replace(/\-\-+/g, '-') // Replace multiple - with single -
    .replace(/^-+/, '') // Trim - from start of text
    .replace(/-+$/, ''); // Trim - from end of text
}

/**
 * Generates a unique slug from a given name
 * Checks if the slug already exists and appends a number if needed
 * @param name The name to convert to a slug
 * @returns A unique slug
 */
export async function generateSlug(name: string): Promise<string> {
  let slug = slugify(name);
  let uniqueSlug = slug;
  let counter = 0;
  
  // Check if slug exists, and if so, append a counter
  while (true) {
    const existingCategory = await Category.findOne({ 
      where: { slug: uniqueSlug } 
    });
    
    if (!existingCategory) {
      break;
    }
    
    counter++;
    uniqueSlug = `${slug}-${counter}`;
  }
  
  return uniqueSlug;
} 