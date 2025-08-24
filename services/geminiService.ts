
import { GoogleGenAI } from "@google/genai";

const API_KEY = process.env.API_KEY;

if (!API_KEY) {
  console.error("API_KEY environment variable not set.");
  // In a real app, you might want to show this error in the UI.
}

const ai = new GoogleGenAI({ apiKey: API_KEY! });

const model = 'gemini-2.5-flash';

export const generateLegalText = async (fileName: string): Promise<string> => {
    if (!API_KEY) {
        return Promise.resolve(`This is placeholder text for ${fileName} because the API key is not configured. This Agreement is made and entered into as of the Effective Date by and between the parties. WHEREAS, the Client wishes to engage the Service Provider to perform certain services; and WHEREAS, the Service Provider has the skills, qualifications, and expertise to perform such services. NOW, THEREFORE, in consideration of the mutual covenants and promises herein contained, the parties agree as follows: 1. Services. The Service Provider agrees to perform the services described in Exhibit A attached hereto (the “Services”). The manner and means by which the Service Provider chooses to complete the Services are in the Service Provider’s sole discretion and control. 2. Term. This Agreement shall commence on the Effective Date and shall continue until the satisfactory completion of the Services, unless earlier terminated as provided in this Agreement.`);
    }

  try {
    const prompt = `Generate a realistic-looking block of text (about 1500-2000 characters) from a legal document related to the topic suggested by the filename: "${fileName}". The text should be dense, contain legal jargon, and simulate a real contract, court filing, or legal brief. Do not use markdown, just output the raw text. Include typical legal document artifacts like section numbers (e.g., "Section 1.1.", "Article II."), but ensure it's a single, continuous block of text without extra formatting.`;
    
    const response = await ai.models.generateContent({
        model,
        contents: prompt
    });

    return response.text;
  } catch (error) {
    console.error('Error generating legal text with Gemini:', error);
    // Fallback to a generic placeholder on API error
    return `Error generating text for ${fileName}. This is placeholder text. This Agreement is made and entered into as of the Effective Date by and between the parties. WHEREAS, the Client wishes to engage the Service Provider to perform certain services; and WHEREAS, the Service Provider has the skills, qualifications, and expertise to perform such services. NOW, THEREFORE, in consideration of the mutual covenants and promises herein contained, the parties agree as follows: 1. Services. The Service Provider agrees to perform the services described in Exhibit A attached hereto (the “Services”). The manner and means by which the Service Provider chooses to complete the Services are in the Service Provider’s sole discretion and control. 2. Term. This Agreement shall commence on the Effective Date and shall continue until the satisfactory completion of the Services, unless earlier terminated as provided in this Agreement.`;
  }
};
